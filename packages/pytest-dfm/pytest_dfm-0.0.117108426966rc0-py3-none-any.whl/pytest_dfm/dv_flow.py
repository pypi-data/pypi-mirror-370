import asyncio
import os
import dataclasses as dc
import logging
from pytest import FixtureRequest
from dv_flow.mgr import PackageLoader, TaskGraphBuilder, TaskSetRunner, SeverityE, TaskMarker
from typing import ClassVar
from .impl.ext_rgy import ExtRgy

@dc.dataclass
class DvFlow(object):
    request: FixtureRequest
    srcdir : str
    tmpdir: str
    builder : TaskGraphBuilder = dc.field(default=None)
    ext_rgy : ExtRgy = dc.field(default_factory=ExtRgy)

    _log : ClassVar = logging.getLogger("DvFlow")

    def __post_init__(self):
        loader = PackageLoader(pkg_rgy=self.ext_rgy)
        self.builder = TaskGraphBuilder(None, self.tmpdir, loader=loader)
        self.srcdir = os.path.dirname(self.request.fspath)
        pass

    def addPackage(self, name, pkgfile):
        """Adds a package to the task graph builder"""
        self.ext_rgy.addPackage(name, pkgfile)

#    def addOverride(self, key, value):
#        self.builder.addOverride(key, value)

    def loadPkg(self, pkgfile):
        """Loads the specified flow.dv file as th root package"""
        loader = PackageLoader(pkg_rgy=self.ext_rgy)
        pkg = loader.load(pkgfile)
        self.builder = TaskGraphBuilder(
            root_pkg=pkg, 
            rundir=os.path.join(self.tmpdir, "rundir"), 
            loader=loader)

    def setEnv(self, env):
        """Sets the environment for the task graph"""
        if self.builder is not None:
            self.builder.setEnv(env)
        else:
            raise Exception("Task graph builder not initialized")

    def mkTask(self, 
                   task_t,
                   name=None,
                   srcdir=None,
                   needs=None,
                   **kwargs):
        """Creates a task of the specified type"""
        return self.builder.mkTaskNode(
            task_t, 
            name=name, 
            srcdir=srcdir, 
            needs=needs, 
            **kwargs)
    
    def runFlow(self, root, task, listener=None, nproc=-1):
        self.loadPkg(root)
        root_task = self.mkTask(task)
        return self.runTask(root_task, listener, nproc)

    def runTask(self, 
                task, 
                listener=None,
                nproc=-1):
        """Executes the specified tree of task nodes"""
        markers = []
        runner = TaskSetRunner(
            self.tmpdir,
            builder=self.builder)

        def local_listener(task, reason):
            if reason == "leave":
                markers.extend(task.result.markers)

        if listener is not None:
            runner.add_listener(listener)
        else:
            runner.add_listener(local_listener)

        if nproc != -1:
            runner.nproc = nproc

        ret = asyncio.run(runner.run(task))

        # Display markers
        for m in markers:
            path = None
            if m.loc is not None:
                path = m.loc.path
                if m.loc.line != -1:
                    path += ":%d" % m.loc.line
                if m.loc.pos != -1:
                    path += ":%d" % m.loc.pos

            if m.severity == SeverityE.Error:
                self._log.error("%s %s" % (m.msg, (path if path is not None else "")))
            elif m.severity == SeverityE.Warning:
                self._log.warning("%s %s" % (m.msg, (path if path is not None else "")))
            elif m.severity == SeverityE.Info:
                self._log.info("%s %s" % (m.msg, (path if path is not None else "")))

        return (runner.status, ret)


