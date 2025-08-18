import sys
import winerror
import argparse

import win32serviceutil
import win32service
import servicemanager

from ._base import BasePlatformService


_STARTUP_TYPE_MAP = {
    "manual": win32service.SERVICE_DEMAND_START,
    "auto": win32service.SERVICE_AUTO_START,
}


# NOTE: obscure bug was found when trying to run installer to update
# and event viewer was open at same time. servicemanager.pyd file becomes locked up.
# turns out event viewer does this. closing event viewer removes this lock.
# see: https://mail.python.org/pipermail/python-win32/2004-December/002736.html


class WindowsPlatformService(BasePlatformService, win32serviceutil.ServiceFramework):
    def __init_subclass__(cls, *args, **kwargs) -> None:
        # these attributes must be set for the pywin32 framework to work
        cls._svc_name_ = cls.name
        cls._svc_display_name_ = cls.title
        cls._svc_description_ = cls.description
        return super().__init_subclass__(*args, **kwargs)

    def SvcDoRun(self) -> None:
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.run()

    def SvcStop(self) -> None:
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop()
        # framework will set as actually stopped when service really does

    def SvcShutdown(self) -> None:
        # handle platform shutdown, shutting down the service immediately
        self.SvcStop()

    def started(self) -> None:
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

    def stopped(self) -> None:
        pass  # handled by pywin32 framework automatically

    @classmethod
    def execute(cls) -> int | None:
        # this handles when windows tries to start the service itself
        if len(sys.argv) == 1:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(cls)
            servicemanager.StartServiceCtrlDispatcher()
        # this handles when we get cmdline input when run from a console
        else:
            # not using handlecmdline func built into pywin32 because was running into
            # some weird issues and because there is a lot of other stuff in those params
            # which may not work cross-platform
            parser = argparse.ArgumentParser(
                prog=cls._svc_display_name_, description=cls._svc_description_
            )
            subparsers = parser.add_subparsers(dest="subcommand", required=True)
            install_parser = subparsers.add_parser(
                "install", description="install the service on this machine"
            )
            install_parser.add_argument(
                "--username",
                type=str,
                default=None,
                help=r"domain\username of the account to run the service under",
            )
            install_parser.add_argument(
                "--password",
                type=str,
                default=None,
                help="password of the account to run the service under",
            )
            subparsers.add_parser(
                "uninstall", description="uninstall the service from the machine"
            )
            subparsers.add_parser(
                "start",
                description="start the service if it is installed or throw error if not",
            )
            subparsers.add_parser(
                "stop",
                description="stop the service if it is installed or throw error if not",
            )
            parser.parse_args()

            args = parser.parse_args(sys.argv[1:])
            rc = 0
            if args.subcommand == "install":
                if (
                    args.username
                    or args.password
                    and not (args.username and args.password)
                ):
                    raise ValueError(
                        "username and password must both be given if either is"
                    )
                try:
                    win32serviceutil.InstallService(
                        pythonClassString=win32serviceutil.GetServiceClassString(cls),
                        serviceName=cls.name,
                        displayName=cls.title,
                        startType=_STARTUP_TYPE_MAP[cls.startup.value],
                        description=cls.description,
                        userName=args.username,
                        password=args.password,
                    )
                except win32service.error as exc:
                    if exc.winerror == winerror.ERROR_SERVICE_EXISTS:
                        # update instead of installing
                        try:
                            win32serviceutil.ChangeServiceConfig(
                                pythonClassString=win32serviceutil.GetServiceClassString(
                                    cls
                                ),
                                serviceName=cls.name,
                                displayName=cls.title,
                                startType=_STARTUP_TYPE_MAP[cls.startup.value],
                                description=cls.description,
                            )
                        except win32service.error as exc:
                            print(f"Error updating service: {exc.strerror}")
                            rc = exc.winerror
                    else:
                        print(f"Error installing service: {exc.strerror}")
                        rc = exc.winerror
            elif args.subcommand == "uninstall":
                try:
                    win32serviceutil.RemoveService(cls.name)
                except win32service.error as exc:
                    print(f"Error uninstalling service: {exc.strerror}")
                    rc = exc.winerror
            elif args.subcommand == "start":
                try:
                    win32serviceutil.StartService(cls.name)
                    win32serviceutil.WaitForServiceStatus(
                        serviceName=cls.name,
                        status=win32service.SERVICE_RUNNING,
                        waitSecs=30,
                    )
                except win32service.error as exc:
                    print(f"Error starting service: {exc.strerror}")
                    rc = exc.winerror
            elif args.subcommand == "stop":
                try:
                    win32serviceutil.StopServiceWithDeps(
                        serviceName=cls.name, waitSecs=30
                    )
                except win32service.error as exc:
                    print(f"Error stopping service: {exc.strerror}")
                    rc = exc.winerror
            else:
                raise ValueError("Invalid command")
            sys.exit(rc)
