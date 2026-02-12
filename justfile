@_list:
    just --list --justfile {{justfile()}}

flatpak-build:
    flatpak-builder --install-deps-from=flathub --force-clean \
        ./build lol.iliazeus.localsend.yaml

flatpak-run:
    flatpak-builder --run ./build lol.iliazeus.localsend.yaml /app/src/main.py
