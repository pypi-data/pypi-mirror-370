# vim:set et sw=4 ts=4:
# SPDX-FileCopyrightText: 2024-present Atri Bhattacharya <atrib@duck.com>
#
# SPDX-License-Identifier: MIT
#
"""tartex module"""

import fnmatch
import json
import logging as log
import math
import os
import re
import sys
import tarfile as tar
from contextlib import suppress
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from rich import print as richprint
from rich.prompt import Prompt

from tartex import _latex
from tartex._parse_args import parse_args

# Auxilliary file extensions to ignore
# taken from latexmk manual:
# https://www.cantab.net/users/johncollins/latexmk/latexmk-480.txt
AUXFILES = [
    ".aux",
    ".bcf",
    ".fls",
    ".idx",
    ".lof",
    ".lot",
    ".out",
    ".toc",
    ".blg",
    ".ilg",
    ".log",
    ".xdv",
    ".fdb_latexmk",
]

# Supplementary files that are usually required as part of tarball
SUPP_REQ = ["bbl", "ind"]

# Allowed tar extensions
TAR_EXT = ["bz2", "gz", "xz"]

# Default compression
TAR_DEFAULT_COMP = "gz"


def strip_tarext(filename):
    """Strip '.tar(.EXT)' from filename"""
    basename = Path(filename)
    if basename.suffix.lstrip(".") in TAR_EXT:
        basename = basename.with_suffix("")
    if basename.suffix == ".tar":
        basename = basename.with_suffix("")
    return basename


def _full_if_not_rel_path(src, dest):
    p = Path(src).resolve()
    with suppress(ValueError):
        p = p.relative_to(dest)
    if p.is_absolute():
        # Here p is only absolute if it cannot be resolved wrt to dest
        log.debug(
            "Cannot resolve %s relative to %s, will use full path",
            src.as_posix(),
            dest.as_posix(),
        )
    return p


def _summary_msg(nfiles, tarname=None):
    """Return summary msg to print at end of run"""

    def _num_tag(n: int):
        return f"[bold]{n} file" + ("s" if n > 1 else "") + "[/]"

    if tarname:
        richprint(
            f"[cyan]Summary: [bold]{tarname}[/] generated with"
            f" {_num_tag(nfiles)}.[/]"
        )
    else:
        richprint(f"[cyan]Summary: {_num_tag(nfiles)} to include.[/]")


class TarTeX:
    """
    Class to help build  a tarball including all source files needed to
    re-compile your LaTeX project."
    """

    # pylint: disable=too-many-instance-attributes

    pkglist_name = "TeXPackages.json"

    def __init__(self, args):
        self.args = parse_args(args)
        log.basicConfig(
            format="[%(levelname)s] %(message)s",
            level=(
                (log.INFO // self.args.verbose)
                if self.args.verbose > 0
                else log.WARN
            ),
        )
        self.cwd = Path.cwd()
        self.main_file = self.args.fname.resolve()
        if self.main_file.suffix not in [".fls", ".tex"]:
            found_file = False
            # Try adding the .fls/.tex suffix to main_file
            for f in [str(self.main_file) + suff for suff in ['.fls', '.tex']]:
                if Path(f).is_file():
                    self.main_file = Path(f)
                    found_file = True
                    break
            if not found_file:
                log.critical(f"Error: File {self.main_file.name}[.tex|.fls] not found.")
                sys.exit(1)

        self.mtime: int
        self.main_pdf = self.main_file.with_suffix(".pdf")
        # Set default tar extension...
        self.tar_ext = TAR_DEFAULT_COMP
        # ..but use specified output's TAR_EXT extension if any...
        if self.args.output:
            self.args.output = self._proc_output_path()

        # ...but overwrite TAR_EXT if tar compression option passed
        if self.args.bzip2:
            self.tar_ext = "bz2"
        if self.args.gzip:
            self.tar_ext = "gz"
        if self.args.xz:
            self.tar_ext = "xz"

        tar_base = (
            Path(f"{self.args.output}.tar")
            if self.args.output
            else Path(self.main_file.stem).with_suffix(".tar")
        )
        self.tar_file = self.cwd / tar_base  # returns tar_base when absolute
        log.debug(
            "Output tarball '%s' will be generated",
            self.tar_file.with_suffix(f".tar.{self.tar_ext}"),
        )

        self.req_supfiles = {}
        self.add_files = self.args.add.split(",") if self.args.add else []
        excludes = self.args.excl.split(",") if self.args.excl else []
        excl_lists = (self.main_file.parent.glob(f"{L}") for L in excludes)

        self.excl_files = [
            f.relative_to(self.main_file.parent).as_posix()
            for L in excl_lists
            for f in L
        ]

        # If .bbl/.ind is missing in source dir, then it is not in
        # self.excl_files (result of globbing files in srcdir) even if the user
        # passes a matching wildcard to exclude it with "-x".
        # Extend self.excl_files specifically in these cases
        for glb in excludes:
            self.excl_files.extend(
                [
                    f
                    for f in [
                        self.main_file.with_suffix(f".{g}") for g in SUPP_REQ
                    ]
                    if fnmatch.fnmatch(f.name, glb)
                ]
            )

        if self.excl_files:
            log.debug(" ".join(excl_lists))
            log.info(
                "List of excluded files: %s",
                ", ".join([Path(x).as_posix() for x in self.excl_files]),
            )

        self.force_tex = self.args.latexmk_tex
        if not self.force_tex:
            # If force_tex is not set by user options,
            # set to ps if source dir contains ps/eps files
            # or to pdf otherwise
            src_ps = [
                str(p)
                for ext in ["eps", "ps"]
                for p in self.main_file.parent.glob(f"**/*.{ext}")
            ]
            self.force_tex = "ps" if src_ps else "pdf"
            log.info(
                "Latexmk will use %slatex for processing, if needed",
                self.force_tex,
            )

        self.pkglist = None

    def add_user_files(self):
        """
        Return list of additional user specified/globbed file paths,
        if they exist
        """
        lof = []
        for fpatt in self.add_files:
            afiles = list(self.main_file.parent.glob(fpatt))
            if not afiles:
                log.warning(
                    "No match corresponding to user specified pattern '%s' for"
                    " additional files",
                    fpatt,
                )
                continue
            lof.extend(afiles)

        return lof

    def bib_file(self):
        """Return relative path to bib file"""
        bibre  = re.compile(r"^\\bibliography\{.*\}")
        bib_name = None
        bstre  = re.compile(r"^\\bibliographystyle\{.*\}")
        bst_name = None
        texf   = self.main_file.with_suffix(".tex")
        with open(texf, encoding="utf-8") as f:
            for line in f:
                m_bib = bibre.search(line)
                m_bst = bstre.search(line)
                if m_bib:
                    bib_name = m_bib.group()
                    continue
                if m_bst:
                    bst_name = m_bst.group()
                    continue
                if bib_name and bst_name:
                    break

        if bib_name:
            bib_name = re.sub(r"^\\bibliography\{", "", bib_name).rstrip("}")
            bib_name += ".bib" if bib_name.split(".")[-1] != ".bib" else ""
        if bst_name:
            bst_name = re.sub(r"^\\bibliographystyle\{", "", bst_name).rstrip("}")
            bst_name += ".bst" if bst_name.split(".")[-1] != ".bst" else ""

        return [Path(f) if Path(f).is_file() else None for f in [bib_name, bst_name]]

    def input_files(self):
        """
        Returns non-system input files needed to compile the main tex file.
        Will try to compile the main tex file using `latexmk` if it cannot find
        the fls file in the same dir.
        """
        if (
            not self.main_file.with_suffix(".fls").exists()
            or self.args.force_recompile
        ):
            with TemporaryDirectory() as compile_dir:
                log.info(
                    "LaTeX recompile forced"
                    if self.args.force_recompile
                    else f"{self.main_file.stem}.fls file not found in"
                    f" {self.main_file.parent.as_posix()}"
                )
                log.info("LaTeX compile directory: %s", compile_dir)
                fls_path = _latex.run_latexmk(
                    self.main_file.with_suffix(".tex"),
                    self.force_tex,
                    compile_dir,
                )
                if self.args.with_pdf:
                    with open(fls_path.with_suffix(".pdf"), "rb") as f:
                        self.pdf_stream = f.read()

                with open(fls_path, encoding="utf-8") as f:
                    deps, pkgs = _latex.fls_input_files(
                        f,
                        self.excl_files,
                        AUXFILES,
                        sty_files=self.args.packages,
                    )

                self.mtime = os.path.getmtime(fls_path)
                self.main_pdf = Path(compile_dir) / self.main_pdf.name
                if self.args.with_pdf:
                    log.info("Add contents as BytesIO: %s", self.main_pdf)
                for ext in SUPP_REQ:
                    if app := self._missing_supp(
                        self.main_file.with_suffix(f".{ext}"), compile_dir, deps
                    ):
                        self.req_supfiles[
                            self.main_file.with_suffix(f".{ext}")
                        ] = app
        else:
            # If .fls exists, this assumes that all INPUT files recorded in it
            # are also included in source dir
            self.mtime = os.path.getmtime(self.main_file.with_suffix(".fls"))

            if self.args.with_pdf:
                try:
                    with open(self.main_pdf, "rb") as f:
                        self.pdf_stream = f.read()
                        log.info("Add file: %s", self.main_pdf.name)
                except FileNotFoundError:
                    log.warning(f"Unable to find '{self.main_pdf.name}' in {self.cwd}, skipping...")
                    self.args.with_pdf = False
            with open(self.main_file.with_suffix(".fls"), encoding="utf8") as f:
                deps, pkgs = _latex.fls_input_files(
                    f, self.excl_files, AUXFILES, sty_files=self.args.packages
                )
                if self.args.packages:
                    self.pkglist = json.dumps(pkgs, cls=SetEncoder).encode(
                        "utf8"
                    )

        if self.args.bib:
            for f in self.bib_file():
                try:
                    deps.append(f.as_posix())
                    log.info("Add file: %s", deps[-1])
                    if re.match(r".bst", f.suffix):
                        pkgs["Local"].add(deps[-1])
                except:
                    pass

        if self.add_files:
            for f in self.add_user_files():
                f_relpath_str = f.relative_to(self.main_file.parent).as_posix()
                if f_relpath_str in deps:
                    log.warning(
                        "Manually included file %s already added", f_relpath_str
                    )
                    continue
                deps.append(f_relpath_str)
                log.info("Add user specified file: %s", f_relpath_str)

        if self.args.packages:
            log.info(
                "System TeX/LaTeX packages used: %s",
                ", ".join(sorted(pkgs["System"]))
            )

            self.pkglist = json.dumps(pkgs, cls=SetEncoder).encode("utf8")
        return deps

    def tar_files(self):
        """
        Generates a tarball consisting of non-system input files needed to
        recompile your latex project.
        """
        self.check_main_file_exists()
        full_tar_name = Path(f"{self.tar_file}.{self.tar_ext}")

        wdir = self.main_file.resolve().parent
        os.chdir(wdir)
        log.debug("Switching working dir to %s", wdir.as_posix())
        if self.args.list:
            file_list = self.input_files()
            if self.args.with_pdf:
                file_list += [self.main_pdf.name]
            self._print_list(file_list)
        else:
            try:
                f = tar.open(full_tar_name, mode=f"x:{self.tar_ext}")
                with f:
                    self._do_tar(f)
                    if self.args.summary:
                        _summary_msg(
                            len(f.getmembers()),
                            _full_if_not_rel_path(full_tar_name, self.cwd),
                        )
            except PermissionError as err:
                log.critical(
                    "Cannot write to %s, %s",
                    full_tar_name.parent,
                    err.strerror.lower(),
                )
                sys.exit(1)
            except FileExistsError:
                try:
                    full_tar_name = self._tar_name_conflict(full_tar_name)
                    # At this stage, there is either a new name for the tar
                    # file or user wants to overwrite existing file. In either
                    # case, calling tar.open() with 'w' mode should be OK.
                    f = tar.open(full_tar_name, mode=f"w:{self.tar_ext}")
                    with f:
                        self._do_tar(f)
                        if self.args.summary:
                            _summary_msg(
                                len(f.getmembers()),
                                _full_if_not_rel_path(full_tar_name, self.cwd),
                            )
                except PermissionError as err:
                    log.critical(
                        "Cannot write to %s, %s",
                        full_tar_name.parent,
                        err.strerror.lower(),
                    )
                    sys.exit(1)
        os.chdir(self.cwd)
        log.debug("Reset working dir to %s", os.getcwd())

    def _tar_name_conflict(self, tpath):
        if self.args.overwrite:
            log.warning(f"Overwriting existing tar file {tpath}")
            return tpath
        richprint(
            "[bold red]A tar file with the same name"
            rf" \[{_full_if_not_rel_path(tpath, self.cwd)}]"
            " already exists[/bold red]"
        )

        owr = Prompt.ask(
            "What would you like to do "
            r"([bold blue]\[O][/bold blue]verwrite /"
            r" [bold green]\[C][/bold green]hoose new name /"
            r" *[bold red]\[Q][/bold red]uit)?"
        )
        if owr.lower() in ["", "q"]:
            richprint(
                "[bold]Not overwriting existing tar file[/bold]\nQuitting",
                file=sys.stderr,
            )
            sys.exit(1)
        elif owr.lower() == "c":
            new_name = Prompt.ask("Enter [bold]new name[/bold] for tar file")
            if (new_ext := new_name.split(".")[-1]) in TAR_EXT:
                self.tar_ext = new_ext
            # If new file is a plain file name, interpret w.r.t. output dir
            if self.args.output and (
                str(Path(new_name)) == Path(new_name).name
            ):
                new_name = Path(self.args.output).with_name(new_name)
            else:
                new_name = self.cwd / Path(new_name).expanduser()
            new_path = new_name.with_name(
                f"{strip_tarext(new_name.name)}.tar.{self.tar_ext}"
            ).resolve()
            if new_path == tpath:
                richprint(
                    "[bold red]Error: New name entered is also the same as"
                    " existing tar file name[/bold red]\nQuitting",
                    file=sys.stderr,
                )
                sys.exit(1)
            elif new_path.exists():
                richprint(
                    "[bold red]Error: A tar file with the same name"
                    rf" \[{_full_if_not_rel_path(new_path, self.cwd)!s}] also"
                    " exists[/bold red]\nQuitting",
                    file=sys.stderr,
                )
                sys.exit(1)
            else:
                log.info("Tar file %s will be generated", new_path.as_posix())
                return new_path
        elif owr.lower() == "o":
            log.warning(f"Overwriting existing tar file {tpath}")
            return tpath
        else:
            richprint(
                "[bold red]Error: Invalid response[/]\nQuitting.",
                file=sys.stderr,
            )
            sys.exit(1)

    def check_main_file_exists(self):
        """Check for the existence of the main tex/fls file."""
        if not Path(self.main_file).exists():
            log.critical("File not found - %s", self.main_file)
            sys.exit(1)

    def _do_tar(self, tar_obj):
        for dep in self.input_files():
            # By now, if the file is still missing, this indicates a .fls file
            # is present in source but some of its INPUT marked entries are
            # not. That is user error and we simply omit the missing file from
            # tarball with a warning
            try:
                tinfo = tar_obj.gettarinfo(dep)
                tinfo.uid = tinfo.gid = 0
                tinfo.uname = tinfo.gname = ""
                tar_obj.addfile(tinfo, open(dep, "rb"))
            except FileNotFoundError:
                log.warning(
                    "Skipping INPUT file '%s', not found amongst sources; try"
                    " forcing a LaTeX recompile ('-F').",
                    dep,
                )

        def _tar_add_bytesio(obj, file_name):
            tinfo = tar_obj.tarinfo(file_name)
            tinfo.size = len(obj)
            tinfo.mtime = self.mtime
            tinfo.uid = tinfo.gid = 0
            tinfo.uname = tinfo.gname = ""
            tar_obj.addfile(tinfo, BytesIO(obj))


        if self.args.packages:
            log.info(
                "Adding list of packages as BytesIO object: %s",
                self.pkglist_name,
            )
            _tar_add_bytesio(self.pkglist, self.pkglist_name)

        for fpath, byt in self.req_supfiles.items():
            log.info("Adding %s as BytesIO object", fpath.name)
            _tar_add_bytesio(byt, fpath.name)
        if self.args.with_pdf:
            _tar_add_bytesio(self.pdf_stream, self.main_pdf.name)


    def _proc_output_path(self):
        """
        Returns the output tar file path (sans any '.tar.?z' suffix) after
        resolving the value passed to '--output' as part of cmdline options.

        Also sets the tar ext if determined from '--output' argument.
        """

        # If self.args.output is absolute, '/' simply returns it as a PosixPath
        out = self.cwd / self.args.output.expanduser()

        if out.is_dir():  # If dir, set to DIR/main.tar.gz
            log.debug("%s is an existing dir", out)
            out = out.joinpath(
                self.main_file.with_suffix(f".tar.{TAR_DEFAULT_COMP}").name
            )
        elif (ext := out.suffix.lstrip(".")) in TAR_EXT:
            self.tar_ext = ext
        else:
            out = out.with_name(f"{out.name}.tar.{TAR_DEFAULT_COMP}")

        out = strip_tarext(out)
        log.debug("Processed output target: %s", self.args.output)
        return out.as_posix()

    def _print_list(self, ls):
        """helper function to print list of files in a pretty format"""
        idx_width = int(math.log10(len(ls))) + 1
        for i, f in enumerate(sorted(ls)):
            richprint(f"{i+1:{idx_width}}. {f}")
        for r in sorted(self.req_supfiles):
            richprint(f"{'*':>{idx_width + 1}} {r.name}")
        if self.args.packages:
            richprint(f"{'*':>{idx_width + 1}} {self.pkglist_name}")
        if self.args.summary:
            _summary_msg(
                len(ls) + len(self.req_supfiles) + (1 if self.pkglist else 0)
            )

    def _missing_supp(self, fpath, tmpdir, deps):
        """Handle missing supplementary file from orig dir, if req"""
        if (
            fpath not in deps  # bbl file not in source dir
            and (Path(tmpdir) / fpath.name).exists()  # Implies it's req
            and fpath not in self.excl_files  # Not explicitly excluded
        ):
            log.debug("Required file '%s' not in source dir", fpath.name)
            log.info(
                "Add contents as BytesIO: %s",
                Path(tmpdir) / fpath.name,
            )
            return (Path(tmpdir) / fpath.name).read_bytes()

        return None


def make_tar():
    """Build tarball with command line arguments processed by argparse"""
    t = TarTeX(sys.argv[1:])
    t.tar_files()


class SetEncoder(json.JSONEncoder):
    """A class to allow JSONEncoder to interpret a set as a list"""

    def default(self, o):
        """
        Convert o (a set) into a sorted list

        :o: set
        :return: list
        """
        return sorted(o)


if __name__ == "__main__":
    make_tar()
