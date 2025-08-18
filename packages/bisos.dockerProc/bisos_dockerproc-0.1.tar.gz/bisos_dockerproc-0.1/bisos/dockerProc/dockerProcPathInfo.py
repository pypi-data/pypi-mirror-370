# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CmndSvc= for
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-u
#+end_org """
####+END:

####+BEGIN: b:prog:file/proclamations :outLevel 1
""" #+begin_org
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of BISOS ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Neda Communications, Inc. Subject to AGPL.
** It is part of BISOS (ByStar Internet Services OS)
** Best read and edited  with Blee in Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /bisos/git/bxRepos/bisos-pip/binsprep/py3/bisos/binsprep/binsprep.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['binsprep'], }
csInfo['version'] = '202409221313'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'binsprep-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/COMEEGA/_nodeBase_/fullUsagePanel-en.org][BISOS COMEEGA Panel]]
Module description comes here.
** Relevant Panels:
** Status: In use with BISOS
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO complete fileName in particulars.
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]

#+end_org """
####+END:

####+BEGIN: b:py3:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

# ####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] *Imports* =Based on Classification=cs-u=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
# ####+END:

import pathlib

####+BEGIN: bx:cs:py3:section :title "Public Classes"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Public Classes*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:class/decl :className "VagBoxPathInfo" :superClass "object" :comment "Abstraction of a  Interface" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /VagBoxPathInfo/  superClass=object =Abstraction of a  Interface=  [[elisp:(org-cycle)][| ]]
#+end_org """
class VagBoxPathInfo(object):
####+END:
    """
** Abstraction of
"""
    _instance = None

    # Singleton using New
    def __new__(cls):
        if cls._instance is None:
            # print('Creating the object')
            cls._instance = super(VagBoxPathInfo, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    def __init__(
            self,
            pkrFileAbsPath: pathlib.Path | None =None,
            boxBaseDir: pathlib.Path | None =None,
            creator: str | None =None,
            provider: str | None =None,
            distro: str | None =None,
            distroRel: str | None =None,
            distroVersion: str | None =None,
            boxCapability: str | None =None,
            cpuArch: str | None =None,
            selector: str | None =None,
    ):
        self._pkrFileAbsPath = pkrFileAbsPath
        self._boxBaseDir = boxBaseDir
        self._creator = creator
        self._provider = provider
        self._distro = distro
        self._distroRel = distroRel
        self._distroVersion = distroVersion
        self._boxCapability = boxCapability
        self._cpuArch = cpuArch
        self._selector = selector

    @property
    def pkrFileAbsPath(self) -> pathlib.Path | None:
        return self._pkrFileAbsPath

    @pkrFileAbsPath.setter
    def pkrFileAbsPath(self, value: pathlib.Path | None,):
        self._pkrFileAbsPath = value

    @property
    def boxBaseDir(self) -> pathlib.Path | None:
        return self._boxBaseDir

    @boxBaseDir.setter
    def boxBaseDir(self, value: pathlib.Path | None,):
        self._boxBaseDir = value

    @property
    def creator(self) -> str | None:
        return self._creator

    @creator.setter
    def creator(self, value: str | None,):
        self._creator = value

    @property
    def provider(self) -> str | None:
        return self._provider

    @provider.setter
    def provider(self, value: str | None):
        self._provider = value

    @property
    def distro(self) -> str | None:
        return self._distro

    @distro.setter
    def distro(self, value: str | None):
        self._distro = value

    @property
    def distroRel(self) -> str | None:
        return self._distroRel

    @distroRel.setter
    def distroRel(self, value: str | None):
        self._distroRel = value

    @property
    def distroVersion(self) -> str | None:
        return self._distroVersion

    @distroVersion.setter
    def distroVersion(self, value: str | None):
        self._distroVersion = value

    @property
    def boxCapability(self) -> str | None:
        return self._boxCapability

    @boxCapability.setter
    def boxCapability(self, value: str | None):
        self._boxCapability = value

    @property
    def cpuArch(self) -> str | None:
        return self._cpuArch

    @cpuArch.setter
    def cpuArch(self, value: str | None):
        self._cpuArch = value

    @property
    def selector(self) -> str | None:
        return self._selector

    @selector.setter
    def selector(self, value: str | None):
        self._selector = value


boxPathInfo = VagBoxPathInfo()

####+BEGIN: bx:cs:py3:section :title "Public Functions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Public Functions*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "vagBoxPathExtractInfo" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /vagBoxPathExtractInfo/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def vagBoxPathExtractInfo(
####+END:
        vagBoxPkrPath: pathlib.Path,
) -> VagBoxPathInfo | None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]

Example:

    Given /bisos/git/bxRepos/bxObjects/bro_vagrantDebianBaseBoxes/qemu/debian/13/trixie/amd64/netinst/us.pkr.hcl

    Derive the following:

    vagBoxPathInfo.creator="bx"
    provider="libvirt"
    distro="debian"
    distroRel="13"
    distroVersion="13.trixie"
    cpuArch="amd64"
    boxScope="netinst"
    selector="us"

    in the above path: bro_vagrantDebianBaseBoxes maps to creator="bx"
    in the above path: provider  maps to provider="libvirt"
    Everything below bro_vagrantDebianBaseBoxes can be ignored.
    mapping of the rest is self evident.

    #+end_org """

    pkrFileAbsPath = vagBoxPkrPath.absolute()   # Important don't .resolve() so that symlinks work.

    if not pkrFileAbsPath.is_file():
        return None

    boxBaseDir = pkrFileAbsPath.parent

    boxPathInfo.pkrFileAbsPath = pkrFileAbsPath
    boxPathInfo.boxBaseDir = boxBaseDir

    path_parts = pkrFileAbsPath.parts

    # Assuming the path structure is fixed and known
    # Example path: /bisos/git/bxRepos/bxObjects/bro_vagrantDebianBaseBoxes/qemu/debian/13/trixie/amd64/netinst/us.pkr.hcl

    # Extracting parts based on the example
    creatorPart = path_parts[-8]  # Hardcoded based on the example
    if creatorPart == "bro_vagrantDebianBaseBoxes":
        creator = "bx"
    else:
        creator = creatorPart

    providerPart = path_parts[-7]  # Assuming 'qemu' is at index 5
    if providerPart == "qemu":
        provider = "libvirt"
    else:
        provider = providerPart

    distro = path_parts[-6]  # Assuming 'debian'
    distroRel = path_parts[-5]  # Assuming '13'
    distroVersion = f"{path_parts[-5]}.{path_parts[-4]}"  # '13.trixie'
    cpuArch = path_parts[-3]  # Assuming 'amd64'
    boxCapability = path_parts[-2]  # Assuming 'netinst'
    selector = path_parts[-1].split('.')[0]  # Assuming us

    # Setting the extracted information to the VagBoxPathInfo instance
    boxPathInfo.creator = creator
    boxPathInfo.provider = provider
    boxPathInfo.distro = distro
    boxPathInfo.distroRel = distroRel
    boxPathInfo.distroVersion = distroVersion
    boxPathInfo.boxCapability = boxCapability
    boxPathInfo.cpuArch = cpuArch
    boxPathInfo.selector = selector

    return boxPathInfo


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
