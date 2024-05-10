# Bincrafters Conan Remote Tool

This tool is something like a locally run proxy server to provide the Conan client with a Conan remote as it expects.


## Install

  * `pip install bincrafters-conan-remote`
  * Or `pip install .` within the git repository.


## Run

  * Start the remote via `bincrafters-conan-remote run`
  * See all command line options via `bincrafters-conan-remote --help`
  * On the Conan client side you need to add a remote that makes use of this remote server. The url structure is something like `http://127.0.0.1:8042/r/github+bincrafters_remote+testing_v-998+bincrafters/` - e.g. `conan remote add inexorgame http://127.0.0.1:8042/r/github+bincrafters_remote+testing_v-998+inexorgame/`


## Limitations

  * Only Conan clients with revisions enabled are supported
  * Features that are covered by both v1 and v2 of the REST API will only be supported via the v2 API
  * Only Conan 1.* is explicitly supported for now, altough the REST API does not seem to be Conan 1/2 specific. So Conan v2 might just work
  * Only Python >= 3.8 is supported. Conan itself supports >= 3.6
  * From the point-of-view of the Conan client this remote is ready-only by design. No upload, no deletion etc.


## TODO

  * Make everything work:
    * conan search
    * conan download
    * conan install
    * get overview conan command / patch / server request that we want to support
  * Write tests for all conan cli command that we want to cover
  * Figure out if the Conan client supports download package downloads from an absolut URL or only relatives one
  * Is the Conan Server Api v2 identical for Conan 1 und 2? If yes, how does Conan determinate packages if they are for 1 or 2? Is the User Agent relevant?
  * Implement a list of official binary package mirrors, we check which mirrors are reachable currently, if one is, we download the binary packages from there, compare checksums, if it matches, we return the response a.k.a offering the binary package download to the conan client, if no mirror is available or checksums don't match we don't return any binary packages available
  * execute tests in CI
  * implement local type: clone git repo, periodically fetch git remote, git switch to selected remote checkout, serve those git files via another fastapi route
  * ~~publish this package via CD on pypi~~
  * explore if we can write a Conan hook, that starts the server automatically when any Conan command gets called. is that possible? there is probably no safe auto-exit event/hook possible?
  * write tool counterpart that generates the static files from an actual running conan server
    * write this somewhat modular, beyond fetching an entire conan server, it should also be possible to only generate the data for a single package -> when we update a package, we can generate the new static files much quicker
