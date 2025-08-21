````{admonition} If you already have Nix set up…
:class: note 

You will need to enable FOSSi Foundations's
[Binary Cache](https://nixos.wiki/wiki/Binary_Cache) manually.

See <https://github.com/fossi-foundation/nix-eda/blob/main/Installation.md> for
more info.

---

If you *do* know what this means, the values are as follows:

```ini
extra-substituters = https://nix-cache.fossi-foundation.org
extra-trusted-public-keys = nix-cache.fossi-foundation.org:3+K59iFwXqKsL7BNu6Guy0v+uTlwsxYQxjspXzqLYQs=
```

Make sure to restart `nix-daemon` after updating `/etc/nix/nix.conf`.

```console
$ sudo pkill nix-daemon
```

````

# Cloning CACE

With git installed, just run the following:

```console
$ git clone https://github.com/fossi-foundation/cace
```

That's it. Whenever you want to use CACE, run `nix-shell` in the repository root
directory and you'll have a full CACE environment. The first time might take
around 10 minutes while binaries are pulled from the cache.

To quickly test your installation, simply run `cace --help` in the nix
shell.
