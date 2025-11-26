{ pkgs }: {
  deps = [
    pkgs.python311Packages.python-telegram-bot
    pkgs.python311Packages.flask
  ];
}