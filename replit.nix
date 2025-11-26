{ pkgs }: {
  deps = [
    pkgs.python310Packages.python-telegram-bot
    pkgs.python310Packages.flask
    pkgs.python310Packages.nest-asyncio   # ← добавь эту строку!
  ];
}