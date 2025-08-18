# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.5] - 2025-08-17

### Added
- Docs: Add sim-to-real workflow ([f1f9f00](https://github.com/AndrejOrsula/space_robotics_bench/commit/f1f9f006b148cb7a3f6d06d97428d1c45fdebe8c)) by @AndrejOrsula
- Waypoint_navigation: Add sim-to-real utils ([1e3a1de](https://github.com/AndrejOrsula/space_robotics_bench/commit/1e3a1ded9026c60aeeea4e29485d7aacafa1b77f)) by @AndrejOrsula
- Add sim-to-real support for all RL integrations ([9f650ef](https://github.com/AndrejOrsula/space_robotics_bench/commit/9f650ef6857846e1caf838749a92a48f7a9a44df)) by @AndrejOrsula
- Add sim-to-real interface ([b003dc3](https://github.com/AndrejOrsula/space_robotics_bench/commit/b003dc3acf7a9bc424d318c7aa529cdc92bc5389)) by @AndrejOrsula
- Add action/observation delays ([51f4272](https://github.com/AndrejOrsula/space_robotics_bench/commit/51f4272f6141841c697108c232b494c612283394)) by @AndrejOrsula
- Add asset type casting ([4e58acd](https://github.com/AndrejOrsula/space_robotics_bench/commit/4e58acd2d750b96370da690c4a8c10b513b6643a)) by @AndrejOrsula
- Add action smoothing wrapper ([8bf600c](https://github.com/AndrejOrsula/space_robotics_bench/commit/8bf600c7355e0f7164005cc20a8ec27f0301f094)) by @AndrejOrsula
- Add XR support and option to select rendering modes ([099e2ec](https://github.com/AndrejOrsula/space_robotics_bench/commit/099e2ec98b5b546d01457ab0c817f230034c4781)) by @AndrejOrsula
- Dreamer: Add "debug" model size ([8551535](https://github.com/AndrejOrsula/space_robotics_bench/commit/8551535eb8e853a2ab732bd97189f4936c04d151)) by @AndrejOrsula
- Docs: Add missing videos for RL workflow ([75de328](https://github.com/AndrejOrsula/space_robotics_bench/commit/75de328c6089988d2c3fef12f3f485a3a03966a2)) by @AndrejOrsula

### Changed
- Bump MSRV to 1.88 ([cea6f7d](https://github.com/AndrejOrsula/space_robotics_bench/commit/cea6f7d60032f160ef9a961044c385134b9f7658)) by @AndrejOrsula
- Docs: Enhance troubleshooting ([8789a23](https://github.com/AndrejOrsula/space_robotics_bench/commit/8789a2399124024dcf23233a230ead70e715bd3b)) by @AndrejOrsula
- CLI: Update with sim-to-real workflows ([fd0d9a2](https://github.com/AndrejOrsula/space_robotics_bench/commit/fd0d9a27b0df6cda9566e362ea3ab6d35b26196d)) by @AndrejOrsula
- Screwdriving: Refactor Ingenuity decor handling ([404b517](https://github.com/AndrejOrsula/space_robotics_bench/commit/404b517b3e7597e9d60eb87f629fd996da8ca654)) by @AndrejOrsula
- Waypoint_navigation: Update task for dynamic pose tracking ([78deed9](https://github.com/AndrejOrsula/space_robotics_bench/commit/78deed973d836fdd59c710dfe3d9d9d31aa0e76f)) by @AndrejOrsula
- Standardize particle handling ([b669bad](https://github.com/AndrejOrsula/space_robotics_bench/commit/b669bad7a4a2088d617aaa2784a90cae8363657c)) by @AndrejOrsula
- Update utils to support real robot workflows ([58288a9](https://github.com/AndrejOrsula/space_robotics_bench/commit/58288a98b8c63f7bcafc795a7e7641c62ce0d834)) by @AndrejOrsula
- Standardize teleop interface naming ([618d6d4](https://github.com/AndrejOrsula/space_robotics_bench/commit/618d6d456bb8fd11c7ee6695e03d85d4c239c991)) by @AndrejOrsula
- Update hyperparams ([a5d42e1](https://github.com/AndrejOrsula/space_robotics_bench/commit/a5d42e1201c601517d225fbbea660f15bb3c96b6)) by @AndrejOrsula
- Update assets ([25430de](https://github.com/AndrejOrsula/space_robotics_bench/commit/25430de24e92c2823dc1b2cae34685c8037f0c5f)) by @AndrejOrsula
- Update dependencies ([a21fd8b](https://github.com/AndrejOrsula/space_robotics_bench/commit/a21fd8bd46d4dbe7f328daa1316893bbd87e866d)) by @AndrejOrsula
- Docker:  Refactor Docker scripts for better argument handling ([a89e9cc](https://github.com/AndrejOrsula/space_robotics_bench/commit/a89e9cc8859944311359c4f7681cab81e4f01918)) by @AndrejOrsula
- Build(deps): bump strum from 0.27.1 to 0.27.2 ([debb2fe](https://github.com/AndrejOrsula/space_robotics_bench/commit/debb2fe7c6abb0cde7aafc76ae7933f3d3b8dbb1)) by @dependabot[bot] in [#71](https://github.com/AndrejOrsula/space_robotics_bench/pull/71)
- Build(deps): bump sysinfo from 0.35.2 to 0.36.0 ([99c3932](https://github.com/AndrejOrsula/space_robotics_bench/commit/99c39329db47c4f3e17d61f312caface539023aa)) by @dependabot[bot] in [#67](https://github.com/AndrejOrsula/space_robotics_bench/pull/67)
- Simplify Omniverse app dependencies ([b64f677](https://github.com/AndrejOrsula/space_robotics_bench/commit/b64f677d73481adf864947b6eb596e2a48597ac4)) by @AndrejOrsula
- Docker: Skip GUI setup if no DISPLAY is set ([57842a4](https://github.com/AndrejOrsula/space_robotics_bench/commit/57842a4229f8ac4c09f21eeb3479010cf5ad8ef1)) by @AndrejOrsula

### Fixed
- Fix seeding of SimForge assets ([2eff3f6](https://github.com/AndrejOrsula/space_robotics_bench/commit/2eff3f6ac63077eaac08371bbe46f642ec50b9e1)) by @AndrejOrsula
- Fix action scaling in WheeledDriveAction ([49ffd84](https://github.com/AndrejOrsula/space_robotics_bench/commit/49ffd84415377e4811b2533594123adf3c90d97c)) by @AndrejOrsula

## [0.0.4] - 2025-06-16

### Added
- GUI: Add workflow selector ([71d1e05](https://github.com/AndrejOrsula/space_robotics_bench/commit/71d1e05567cfe01051c772af9e47d804371db83c)) by @AndrejOrsula
- Add Resilience lander ([ba3a067](https://github.com/AndrejOrsula/space_robotics_bench/commit/ba3a067f5c33ef80d0509a6ffd3f42d788bc3cc6)) by @AndrejOrsula
- Test: Add workflow for performance evaluation ([b24ce00](https://github.com/AndrejOrsula/space_robotics_bench/commit/b24ce00d1f7c98b0132a0ec5603ef593247f9868)) by @AndrejOrsula
- Waypoint_navigation: Add new task ([a390447](https://github.com/AndrejOrsula/space_robotics_bench/commit/a390447d3d4aa4cd5c673a8b24f6fd3ecee64b11)) by @AndrejOrsula
- Rendezvous: Add new task ([95147fa](https://github.com/AndrejOrsula/space_robotics_bench/commit/95147fa262259c2149b94079d1eef070a02948fc)) by @AndrejOrsula
- Screwdriving: Add new task ([04e1789](https://github.com/AndrejOrsula/space_robotics_bench/commit/04e1789d77c0e5d95f17d6b466aa1ec102a0cba2)) by @AndrejOrsula
- Orbital_evasion: Add fuel management ([9ed1a67](https://github.com/AndrejOrsula/space_robotics_bench/commit/9ed1a67604143efb1dae9af7df5d8cf883511284)) by @AndrejOrsula
- Landing: Add reward clamping for the angular velocity term ([dd6cff4](https://github.com/AndrejOrsula/space_robotics_bench/commit/dd6cff40900165cea081c64227d4fa6bf959afd6)) by @AndrejOrsula
- Add missing hyperparameters ([0b82fba](https://github.com/AndrejOrsula/space_robotics_bench/commit/0b82fbaad2718a19836f82ac686c71cf7cf3722b)) by @AndrejOrsula
- Dreamer: Support logging of videos with arbitrary number of channels ([5a54c15](https://github.com/AndrejOrsula/space_robotics_bench/commit/5a54c1561c9bdd925398075af3bc00334c00f8e5)) by @AndrejOrsula
- Add event for pose randomization ([a21e873](https://github.com/AndrejOrsula/space_robotics_bench/commit/a21e873c1bacf680378a634927edef4a6478acc9)) by @AndrejOrsula
- Add support for u8 image observations ([34cc96a](https://github.com/AndrejOrsula/space_robotics_bench/commit/34cc96a32b0f0d66057d0a3c7ab6adb21e43f582)) by @AndrejOrsula
- Add multi-env support for particle utils ([2ec80a1](https://github.com/AndrejOrsula/space_robotics_bench/commit/2ec80a1177fbe1360aa747df7bbfd2c41507a7db)) by @AndrejOrsula
- Support action spaces with all data types ([e150b3d](https://github.com/AndrejOrsula/space_robotics_bench/commit/e150b3d547ec3e5ee6b2d7cff0ffc6cf42b4858e)) by @AndrejOrsula
- Add dummy action group ([408a4b1](https://github.com/AndrejOrsula/space_robotics_bench/commit/408a4b1b59acd84b19bcb312c2b8a27be5a68320)) by @AndrejOrsula
- Add orjson to dependencies ([24671d1](https://github.com/AndrejOrsula/space_robotics_bench/commit/24671d1560ddad67a8e5b5dd25319eda8cff33b4)) by @AndrejOrsula
- Add support for ground plane scenery with non-stacked envs ([4d6c03d](https://github.com/AndrejOrsula/space_robotics_bench/commit/4d6c03db96c317edab2325564c450e63519c7925)) by @AndrejOrsula
- Add SpaceX Starship and Super Heavy ([ac8a1fa](https://github.com/AndrejOrsula/space_robotics_bench/commit/ac8a1faaf2bc71a3fb510061f743edbcda085593)) by @AndrejOrsula
- Docs: Add link to Docker Hub repository ([22fec40](https://github.com/AndrejOrsula/space_robotics_bench/commit/22fec40cbcf4508508152b52484375ecea074438)) by @AndrejOrsula

### Changed
- Bump to 0.0.4 ([8fd170c](https://github.com/AndrejOrsula/space_robotics_bench/commit/8fd170ce242d3f03973fb8ad53b175bb3b438765)) by @AndrejOrsula
- Update assets ([0b4c6cf](https://github.com/AndrejOrsula/space_robotics_bench/commit/0b4c6cfeb861a76c4629f0841c24aaf51ad19f7c)) by @AndrejOrsula
- Docs: Update robots and tasks ([fbd8968](https://github.com/AndrejOrsula/space_robotics_bench/commit/fbd89688138ba0a07e71f8a40543e537e6ec29d1)) by @AndrejOrsula
- Docs: Update usage based on new task defaults ([36dc86e](https://github.com/AndrejOrsula/space_robotics_bench/commit/36dc86ef2b3265ecf5af67c733caa231b3b64f03)) by @AndrejOrsula
- Docs: Simplfy CLI args in examples ([691cb97](https://github.com/AndrejOrsula/space_robotics_bench/commit/691cb97b2901ca16d2ba348c113edd452dc72c4b)) by @AndrejOrsula
- Sb3: Separate tensorboard and wandb enabling parameter ([2554358](https://github.com/AndrejOrsula/space_robotics_bench/commit/2554358d95c35f9aabc3a6f03f378d87d3fde43a)) by @AndrejOrsula
- Separate linear and angular velocity scale for wheeled drive action ([3dc3b98](https://github.com/AndrejOrsula/space_robotics_bench/commit/3dc3b98df656d426c39625118bd81728746c6944)) by @AndrejOrsula
- Bump MSRV to 1.87 ([5e6a98f](https://github.com/AndrejOrsula/space_robotics_bench/commit/5e6a98f76db255da0a4e42b1da8ab1d766a6c084)) by @AndrejOrsula
- CLI: Update entrypoint ([a4134e1](https://github.com/AndrejOrsula/space_robotics_bench/commit/a4134e1a3323dca403bb11f230f57a01381cc479)) by @AndrejOrsula
- GUI: Enhance implementation and improve configurability ([f2837e9](https://github.com/AndrejOrsula/space_robotics_bench/commit/f2837e901821d23968c032d8a706e3b4af5b5f74)) by @AndrejOrsula
- Mobile_debris_capture: Implement task ([c1ccb71](https://github.com/AndrejOrsula/space_robotics_bench/commit/c1ccb71116984814b73db4111591aeee7a033c1b)) by @AndrejOrsula
- Velocity_tracking: Generalize for non-legged robots ([9314b56](https://github.com/AndrejOrsula/space_robotics_bench/commit/9314b56a5b2058398730910ef1e0f089b4e331ea)) by @AndrejOrsula
- Excavation: Refactor into a static setting ([1fdc3d7](https://github.com/AndrejOrsula/space_robotics_bench/commit/1fdc3d7bb81f0c5bce0f547a7769fb3819adedae)) by @AndrejOrsula
- Update task templates ([13bd2b6](https://github.com/AndrejOrsula/space_robotics_bench/commit/13bd2b60c14161cff409cb83c83f09f8f0677081)) by @AndrejOrsula
- Solar_panel_assembly: Update rewards ([6a8d51f](https://github.com/AndrejOrsula/space_robotics_bench/commit/6a8d51f4ab6a7b33f410ef3333e9ed0e8ce2b368)) by @AndrejOrsula
- Sample_collection: Update default domain to Mars and add more reward terms ([5e82ae4](https://github.com/AndrejOrsula/space_robotics_bench/commit/5e82ae4e3875aed15082131a332bd19e7c07453f)) by @AndrejOrsula
- Peg_in_hole_assembly: Update reward weights ([4c14ec2](https://github.com/AndrejOrsula/space_robotics_bench/commit/4c14ec23b5a85855349bd986dc62948d55e93a72)) by @AndrejOrsula
- Debris_capture: Update task and assets ([4107382](https://github.com/AndrejOrsula/space_robotics_bench/commit/410738262a76c8ded52c9f37605576089e455750)) by @AndrejOrsula
- Update assets ([7589133](https://github.com/AndrejOrsula/space_robotics_bench/commit/7589133efbf0fc2fa1bb3602b1b43d3c45f475e6)) by @AndrejOrsula
- Streamline teleop and GUI interfaces ([f75760e](https://github.com/AndrejOrsula/space_robotics_bench/commit/f75760e04bc52d0be128d8c277c92afedf96add8)) by @AndrejOrsula
- Refactor task registration ([f5e925a](https://github.com/AndrejOrsula/space_robotics_bench/commit/f5e925a73b2d9a7df51928e6a0e78f5955d2dd0b)) by @AndrejOrsula
- Streamline base env configs ([22831b7](https://github.com/AndrejOrsula/space_robotics_bench/commit/22831b7c143135b014ab950c05d79a7e9cf32c7a)) by @AndrejOrsula
- Refactor visual env extension configs ([c00acc7](https://github.com/AndrejOrsula/space_robotics_bench/commit/c00acc7dcc7c86367829d4a8ba0411989fcd3107)) by @AndrejOrsula
- Update logic for physics VRAM allocation and skydome handling ([893a3a6](https://github.com/AndrejOrsula/space_robotics_bench/commit/893a3a6c822a785c5c969a7671e7c1236e2e5ddb)) by @AndrejOrsula
- Update action group name handling ([e0b449c](https://github.com/AndrejOrsula/space_robotics_bench/commit/e0b449caaf1d57775bf030843f1159adb78d9e0c)) by @AndrejOrsula
- Update command mapping of OSC action group ([29c4877](https://github.com/AndrejOrsula/space_robotics_bench/commit/29c4877e92a181925085128a2c22c05006473a8b)) by @AndrejOrsula
- Update asset name handling and introduce the Pedestal object type ([d3ee2b5](https://github.com/AndrejOrsula/space_robotics_bench/commit/d3ee2b55ce302efd90696870a99fbb04491adda3)) by @AndrejOrsula
- Refactor offline cache management ([b94e938](https://github.com/AndrejOrsula/space_robotics_bench/commit/b94e938601b0e746de0b24dffd48c664f8407491)) by @AndrejOrsula
- Docker: Update dev dependency revisions ([c45dc75](https://github.com/AndrejOrsula/space_robotics_bench/commit/c45dc756fcbc0ed8457a74e22b32acd58979a810)) by @AndrejOrsula
- Deny: Allow CDLA-Permissive-2.0 license ([6e1dc59](https://github.com/AndrejOrsula/space_robotics_bench/commit/6e1dc5996b5743359b89d0f422db46ce4e27853b)) by @AndrejOrsula
- Pre-commit: Update repos ([441f30b](https://github.com/AndrejOrsula/space_robotics_bench/commit/441f30b3afc2849644c42ab48daedf30e2e5b322)) by @AndrejOrsula
- Build(deps): bump winit from 0.30.10 to 0.30.11 ([266b92f](https://github.com/AndrejOrsula/space_robotics_bench/commit/266b92fa8bbbf48362cc0b808fbd6b195b1a930f)) by @dependabot[bot] in [#65](https://github.com/AndrejOrsula/space_robotics_bench/pull/65)
- Docs: Update video links ([ba5788c](https://github.com/AndrejOrsula/space_robotics_bench/commit/ba5788cc45901988b5d7814e3d133fff30dc8bbb)) by @AndrejOrsula
- Build(deps): bump sysinfo from 0.35.0 to 0.35.1 ([6d59152](https://github.com/AndrejOrsula/space_robotics_bench/commit/6d59152ce2e040e106bad045551028bf3b347e45)) by @dependabot[bot] in [#64](https://github.com/AndrejOrsula/space_robotics_bench/pull/64)
- Build(deps): bump astral-sh/setup-uv from 5 to 6 ([7d5bff5](https://github.com/AndrejOrsula/space_robotics_bench/commit/7d5bff5d8e2fce44c586a5537b3853962c4b06be)) by @dependabot[bot] in [#57](https://github.com/AndrejOrsula/space_robotics_bench/pull/57)
- Build(deps): bump chrono from 0.4.40 to 0.4.41 ([187fb82](https://github.com/AndrejOrsula/space_robotics_bench/commit/187fb8217a0c93864f542428b0e62697024af487)) by @dependabot[bot] in [#61](https://github.com/AndrejOrsula/space_robotics_bench/pull/61)
- Build(deps): bump sysinfo from 0.34.2 to 0.35.0 ([2ea149d](https://github.com/AndrejOrsula/space_robotics_bench/commit/2ea149de6a8151d4e8803ad78ccb9e0b800d6350)) by @dependabot[bot] in [#60](https://github.com/AndrejOrsula/space_robotics_bench/pull/60)
- Build(deps): bump nix from 0.29.0 to 0.30.1 ([2705ead](https://github.com/AndrejOrsula/space_robotics_bench/commit/2705eade71f610b7a8bfb8d6d8f906af7173a4f9)) by @dependabot[bot] in [#59](https://github.com/AndrejOrsula/space_robotics_bench/pull/59)
- Build(deps): bump winit from 0.30.9 to 0.30.10 ([537f804](https://github.com/AndrejOrsula/space_robotics_bench/commit/537f804d6903898673a4796c894687305e18fdc9)) by @dependabot[bot] in [#58](https://github.com/AndrejOrsula/space_robotics_bench/pull/58)
- Build(deps): bump r2r from 0.9.4 to 0.9.5 ([ca8f566](https://github.com/AndrejOrsula/space_robotics_bench/commit/ca8f5660339b852ac7b132fc52a67b04581e45ab)) by @dependabot[bot] in [#56](https://github.com/AndrejOrsula/space_robotics_bench/pull/56)
- Standardize finite horizon across tasks ([0c35a59](https://github.com/AndrejOrsula/space_robotics_bench/commit/0c35a5985b6014ae19c9a4eb4f6aff5b7556a55d)) by @AndrejOrsula
- Generalize landing task for any orbital robot ([08f0be7](https://github.com/AndrejOrsula/space_robotics_bench/commit/08f0be73317368be4e0ab67b5234ae1f925b470a)) by @AndrejOrsula
- Use persistent setting for Nucleus path ([b81c7fa](https://github.com/AndrejOrsula/space_robotics_bench/commit/b81c7fa4d22294c3a7bb200e002fde247bf12ac3)) by @AndrejOrsula
- Update changelog for version 0.0.3 ([e496652](https://github.com/AndrejOrsula/space_robotics_bench/commit/e496652b941dbda875e0a67f7e6aea17b3d8dc52)) by @AndrejOrsula

### Fixed
- Fix command mapping of binary joint velocity action group ([9427cac](https://github.com/AndrejOrsula/space_robotics_bench/commit/9427cac565b5d1fb1ff997792b477f636b4b22fd)) by @AndrejOrsula
- Fix wheeled drive for parallel envs ([712c517](https://github.com/AndrejOrsula/space_robotics_bench/commit/712c517efb57759153fc8f51aa2351f577622bcd)) by @AndrejOrsula
- Fix wheel drive joint order for Leo Rover ([d683641](https://github.com/AndrejOrsula/space_robotics_bench/commit/d683641fe4131f155ef7a33f3c73d0dda5ca5bb6)) by @AndrejOrsula
- Fix wheeled drive action name in ROS interface ([f2b519b](https://github.com/AndrejOrsula/space_robotics_bench/commit/f2b519b7e63dd6aa3b00443246869c11a9ac02d1)) by @AndrejOrsula
- Docs: Fix environment name ([429de9f](https://github.com/AndrejOrsula/space_robotics_bench/commit/429de9f43f319b8cbafdb4d051a06193823ffa8e)) by @AndrejOrsula

## [0.0.3] - 2025-04-01

### Added
- Add landing task ([59f87a9](https://github.com/AndrejOrsula/space_robotics_bench/commit/59f87a98b920cc7a13831257886b9df9731ecc6b)) by @AndrejOrsula
- Add thrust action term and group ([3e98a74](https://github.com/AndrejOrsula/space_robotics_bench/commit/3e98a7460af03470f3ce2676a2b2193a224328fe)) by @AndrejOrsula
- Add support for OSC action term ([152973b](https://github.com/AndrejOrsula/space_robotics_bench/commit/152973b42a4e84e81181cd00dbf496e9013ec099)) by @AndrejOrsula
- Git-cliff: Add commits to the changelog ([6521a4a](https://github.com/AndrejOrsula/space_robotics_bench/commit/6521a4a2ae2c213086fd2a01412756ef93b352f1)) by @AndrejOrsula

### Changed
- Bump to 0.0.3 ([a1afc29](https://github.com/AndrejOrsula/space_robotics_bench/commit/a1afc2904fa7bb82ee85d217e9ac912e048fb3e9)) by @AndrejOrsula
- Docs: Update envs, robots, attributes ([73b6462](https://github.com/AndrejOrsula/space_robotics_bench/commit/73b64622f1cb7a6aa168be91354cf71dee2f85b1)) by @AndrejOrsula
- Improve default hyperparameters of Dreamer ([7a97996](https://github.com/AndrejOrsula/space_robotics_bench/commit/7a97996a3ca25939e3a6398db86ee51766a6eeb5)) by @AndrejOrsula
- Update assets ([7988615](https://github.com/AndrejOrsula/space_robotics_bench/commit/7988615ab3c4b2ec371ea26a7f7ce9c056f793ab)) by @AndrejOrsula
- Tune peg_in_hole rewards ([5144243](https://github.com/AndrejOrsula/space_robotics_bench/commit/51442431629760fd669d3451ebfb0cba338ec83f)) by @AndrejOrsula
- Update environment and agent rates in base environments ([cde5eb5](https://github.com/AndrejOrsula/space_robotics_bench/commit/cde5eb5dc17a4c507017b54713baa1fc393cd1fd)) by @AndrejOrsula
- Update skydome asset directory path ([5c1efee](https://github.com/AndrejOrsula/space_robotics_bench/commit/5c1efee9006d30033a30a5ee0f0a2d873f7ea75d)) by @AndrejOrsula
- Tests: Skip CLI agent train test ([b523ef4](https://github.com/AndrejOrsula/space_robotics_bench/commit/b523ef4c8b90d5f271cc66526b7d290a98696fa6)) by @AndrejOrsula
- Standardize teleop device sensitivity ([288f8eb](https://github.com/AndrejOrsula/space_robotics_bench/commit/288f8ebffec6766772b936af1c9e80ab6b786cd8)) by @AndrejOrsula
- Docker: Update development script with DEBUG_VIS environ ([3b46457](https://github.com/AndrejOrsula/space_robotics_bench/commit/3b46457cdfdc55387af41d39cb9bbe2e1b7e8402)) by @AndrejOrsula
- Update base events and skydomes ([d8172d2](https://github.com/AndrejOrsula/space_robotics_bench/commit/d8172d22a99eb121f2f9a513eb2dc3e4d26f5d59)) by @AndrejOrsula
- Autoreset environment instances that explode due to physics ([ed88f2a](https://github.com/AndrejOrsula/space_robotics_bench/commit/ed88f2aa5d59ac51dcfd575f38fc9d7f6ef7060b)) by @AndrejOrsula
- GiGeneralize action term for all wheeled robots ([c5b38e8](https://github.com/AndrejOrsula/space_robotics_bench/commit/c5b38e88a75e07d012ec078da199f4061da26740)) by @AndrejOrsula
- Docker: Mount Omniverse data volume ([502d5b3](https://github.com/AndrejOrsula/space_robotics_bench/commit/502d5b37ee48003eec5e55f425b047360dc4dcac)) by @AndrejOrsula
- Build(deps): bump image from 0.25.5 to 0.25.6 ([eab74fc](https://github.com/AndrejOrsula/space_robotics_bench/commit/eab74fc93b74a19f9641fe632a340edb8864f82f)) by @dependabot[bot] in [#55](https://github.com/AndrejOrsula/space_robotics_bench/pull/55)
- Build(deps): bump sysinfo from 0.33.1 to 0.34.1 ([8db4e77](https://github.com/AndrejOrsula/space_robotics_bench/commit/8db4e7762cfd3a5d1446f1d5d4244ed6f52d6a42)) by @dependabot[bot] in [#54](https://github.com/AndrejOrsula/space_robotics_bench/pull/54)
- Build(deps): bump typed-builder from 0.20.1 to 0.21.0 ([a2d90a7](https://github.com/AndrejOrsula/space_robotics_bench/commit/a2d90a7231e466e252295f6b1daa4da27dcb3bba)) by @dependabot[bot] in [#53](https://github.com/AndrejOrsula/space_robotics_bench/pull/53)

### Fixed
- Fix naming of IMU visualization marker ([4558a28](https://github.com/AndrejOrsula/space_robotics_bench/commit/4558a28c415843ebf56ee0e6937906be9be65eaf)) by @AndrejOrsula
- Fix contact sensor ([4e3cd28](https://github.com/AndrejOrsula/space_robotics_bench/commit/4e3cd289a6e4ae53461889333e4fcf8ac5478107)) by @AndrejOrsula

## [0.0.2] - 2025-03-20

### Added
- Add git-cliff configuration ([ed79c90](https://github.com/AndrejOrsula/space_robotics_bench/commit/ed79c90d3d1494e4d6be5bac6f412b5e46be192d)) by @AndrejOrsula
- Add templates for mobile manipulation tasks ([6dcf11a](https://github.com/AndrejOrsula/space_robotics_bench/commit/6dcf11a1cdd36784c14a42c37b1fbe85f203d960)) by @AndrejOrsula
- Docker: Add option to ensure Docker and NVIDIA toolkit are installed ([4f0ce88](https://github.com/AndrejOrsula/space_robotics_bench/commit/4f0ce88c5cd14ff98cd91b89606b67f3a8fdd20e)) by @AndrejOrsula
- Devcontainer: Add default extensions ([6b2bc4d](https://github.com/AndrejOrsula/space_robotics_bench/commit/6b2bc4d52cdb74fa787e062d2185d45a362f299f)) by @AndrejOrsula

### Changed
- Bump to 0.0.2 ([b0a8a4b](https://github.com/AndrejOrsula/space_robotics_bench/commit/b0a8a4bc3c6ec40d41b53a89ce9da30319d13a4f)) by @AndrejOrsula
- Docs: Update towards 0.0.2 ([bf4fdb6](https://github.com/AndrejOrsula/space_robotics_bench/commit/bf4fdb610e301e464c5a8081169b13b19b2b36d5)) by @AndrejOrsula
- Bump MSRV to 1.84 ([bdceba6](https://github.com/AndrejOrsula/space_robotics_bench/commit/bdceba6fae7c292d02af3597bcef2a1ab1c99c6c)) by @AndrejOrsula
- Update dependencies (Python & Rust) ([9eea79d](https://github.com/AndrejOrsula/space_robotics_bench/commit/9eea79d00f97ba5cdfe5c996e5f56743388dfaf0)) by @AndrejOrsula
- Deny: Ignore RUSTSEC-2024-0436 ([22ee4b3](https://github.com/AndrejOrsula/space_robotics_bench/commit/22ee4b3045fbada214ebc6c0282a7d728db17bf4)) by @AndrejOrsula
- Docker: Update commits of dev dependencies ([3b69be8](https://github.com/AndrejOrsula/space_robotics_bench/commit/3b69be80ab65ff804a734050d35b8a70c8f92ae0)) by @AndrejOrsula
- Tests: Update to match CLI changes ([02e1c56](https://github.com/AndrejOrsula/space_robotics_bench/commit/02e1c5647c1249b5e144b54b85452c92cccd45e1)) by @AndrejOrsula
- CLI: Streamline usage for readable documentation ([1265f8d](https://github.com/AndrejOrsula/space_robotics_bench/commit/1265f8d163e09ee1a94d9c699907394daab57130)) by @AndrejOrsula
- Locomotion_velocity_tracking: Adjust reward ([4755ec8](https://github.com/AndrejOrsula/space_robotics_bench/commit/4755ec8a1d0cd23b85185a1c2e0e62a8627d436c)) by @AndrejOrsula
- Mobile_debris_capture: Use default robot of the base environment class ([7b00c2e](https://github.com/AndrejOrsula/space_robotics_bench/commit/7b00c2e98c125feed02c9c3dd53f412aac82376e)) by @AndrejOrsula
- Orbital_evasion: Update observation and reward ([578407a](https://github.com/AndrejOrsula/space_robotics_bench/commit/578407a4c818c2e53103a352c61acc5340e0f905)) by @AndrejOrsula
- Excavation: Default to Spot robot mobile base ([a96a135](https://github.com/AndrejOrsula/space_robotics_bench/commit/a96a135bd7009d9a3ebaa162e8760062c0416572)) by @AndrejOrsula
- Refactor environment classes to improve naming consistency across manipulation tasks ([f7176f2](https://github.com/AndrejOrsula/space_robotics_bench/commit/f7176f2b8205f71ef6a5beb8c7ee2593770d7af4)) by @AndrejOrsula
- Simplify base parameter naming in environment config ([1e996e5](https://github.com/AndrejOrsula/space_robotics_bench/commit/1e996e5aac92233dc4c3e0bbae127f03fb4d69b3)) by @AndrejOrsula
- CLI: Improve command-line overrides for environment config ([1f1895f](https://github.com/AndrejOrsula/space_robotics_bench/commit/1f1895fcfc5d909e009d2ad652167f8a2878de88)) by @AndrejOrsula
- Improve asset configuration consistency ([71746aa](https://github.com/AndrejOrsula/space_robotics_bench/commit/71746aa21b57ce0a8a81f8abf1d29ff916898e6b)) by @AndrejOrsula
- Docker: Update the default development volumes ([7acd717](https://github.com/AndrejOrsula/space_robotics_bench/commit/7acd71728e56f08692a9d4b0f4bd4751b0affa87)) by @AndrejOrsula
- Docker: Ensure assets are initialized when building the image ([dbd70fe](https://github.com/AndrejOrsula/space_robotics_bench/commit/dbd70fe9e6c7b45b8908666982d4a7b6de2da1bc)) by @AndrejOrsula
- Update installation scripts ([69b6227](https://github.com/AndrejOrsula/space_robotics_bench/commit/69b6227fe95ea6a09df747c6458e6b263ea396ab)) by @AndrejOrsula
- CI: Checkout submodules recursively to build Docker with assets ([3b351d7](https://github.com/AndrejOrsula/space_robotics_bench/commit/3b351d73c4c64501b1bee1fa2bdbe10332355c68)) by @AndrejOrsula
- Build(deps): bump typed-builder from 0.20.0 to 0.20.1 ([f91220d](https://github.com/AndrejOrsula/space_robotics_bench/commit/f91220de5bd8eab9ff41e505bc806cd10699bd5a)) by @dependabot[bot] in [#52](https://github.com/AndrejOrsula/space_robotics_bench/pull/52)
- Build(deps): bump egui_extras from 0.31.0 to 0.31.1 ([a7691b9](https://github.com/AndrejOrsula/space_robotics_bench/commit/a7691b91e7d0698d34d80729502cf1d6738f88e8)) by @dependabot[bot] in [#51](https://github.com/AndrejOrsula/space_robotics_bench/pull/51)
- Build(deps): bump eframe from 0.31.0 to 0.31.1 ([03615af](https://github.com/AndrejOrsula/space_robotics_bench/commit/03615af8960557a879b780d8f9376375acbd82c6)) by @dependabot[bot] in [#48](https://github.com/AndrejOrsula/space_robotics_bench/pull/48)
- Build(deps): bump serde from 1.0.218 to 1.0.219 ([0b80920](https://github.com/AndrejOrsula/space_robotics_bench/commit/0b80920086b57bb074e910d23251c471b696f535)) by @dependabot[bot] in [#49](https://github.com/AndrejOrsula/space_robotics_bench/pull/49)

### Fixed
- Correct action term/group naming ([7b30546](https://github.com/AndrejOrsula/space_robotics_bench/commit/7b305467f72bbf84509a267b3fa35968bd082a00)) by @AndrejOrsula

### Removed
- Remove redundant event ([92e4f7d](https://github.com/AndrejOrsula/space_robotics_bench/commit/92e4f7d44235816eebe02b9d642340fe66285cc7)) by @AndrejOrsula

## [0.0.1] - 2025-03-04

### Added
- Add barebones mobile_debris_capture task ([a387421](https://github.com/AndrejOrsula/space_robotics_bench/commit/a3874214f2564f96ef6d1bb969b5aaa5188343d4)) by @AndrejOrsula
- Add barebones excavation task ([9438761](https://github.com/AndrejOrsula/space_robotics_bench/commit/94387612a784b1f449d98dce3a3ea9ff3a61e07f)) by @AndrejOrsula
- Add orbital_evasion task ([fab2b5c](https://github.com/AndrejOrsula/space_robotics_bench/commit/fab2b5cd8a9025f0ae0f619d48c4b88121e8f8d6)) by @AndrejOrsula
- Add locomotion_velocity_tracking task ([1665201](https://github.com/AndrejOrsula/space_robotics_bench/commit/16652019b9497cd5d50cc0ac0bf097a95804180b)) by @AndrejOrsula
- Add solar_panel_assembly task ([4867c6b](https://github.com/AndrejOrsula/space_robotics_bench/commit/4867c6b1b349f73423417b23130abd5d1e360876)) by @AndrejOrsula
- Add peg_in_hole_assembly task ([bdb4113](https://github.com/AndrejOrsula/space_robotics_bench/commit/bdb411350ac00f4d32b34f6907e8fa0c20b6c3c7)) by @AndrejOrsula
- Add sample_collection task ([21e09d1](https://github.com/AndrejOrsula/space_robotics_bench/commit/21e09d15c05e3e34151c310f09a9e7ac99f8553f)) by @AndrejOrsula
- Add debris_capture task ([b73a09c](https://github.com/AndrejOrsula/space_robotics_bench/commit/b73a09ccc2ba7702e169c7d8ebc7aee9a60382e7)) by @AndrejOrsula
- Add basic tests ([764fbb8](https://github.com/AndrejOrsula/space_robotics_bench/commit/764fbb8336e4eb11f13cf52ed159cf09095a6336)) by @AndrejOrsula
- Add unified entrypoint script ([ab35b1b](https://github.com/AndrejOrsula/space_robotics_bench/commit/ab35b1b66020101a8c8a7d1786f19c93657af07d)) by @AndrejOrsula
- Add config and hyparparam utils ([444c99f](https://github.com/AndrejOrsula/space_robotics_bench/commit/444c99ff0a26538030a26913eb0eac9036999e95)) by @AndrejOrsula
- Add mobile manipulation base envs ([13d37ca](https://github.com/AndrejOrsula/space_robotics_bench/commit/13d37ca44323fa3b4c000e9ce4b3c67fbbce7152)) by @AndrejOrsula
- Add mobile manipulation base envs ([5eac2a8](https://github.com/AndrejOrsula/space_robotics_bench/commit/5eac2a8592a9a61a00cdda13d935a17913cf53a2)) by @AndrejOrsula
- Add manipulation base env and task template ([486da35](https://github.com/AndrejOrsula/space_robotics_bench/commit/486da35822a82b8e1c0762d1820e5512b2ab50a0)) by @AndrejOrsula
- Add ROS 2 interface ([7028fc7](https://github.com/AndrejOrsula/space_robotics_bench/commit/7028fc7e574762342560d23ec6c46eb9ac1b973c)) by @AndrejOrsula
- Add skrl integration ([52cde70](https://github.com/AndrejOrsula/space_robotics_bench/commit/52cde701564dfe0fde84bf0c2017e1ec43aab070)) by @AndrejOrsula
- Add SB3 and SBX integrations ([7cf19a3](https://github.com/AndrejOrsula/space_robotics_bench/commit/7cf19a3f761cf1c8c8593252d8b8fdfd85aebdff)) by @AndrejOrsula
- Add Dreamer integration ([56a1ccf](https://github.com/AndrejOrsula/space_robotics_bench/commit/56a1ccf5f51fc7065eec4cc2a196dd87fddc0f80)) by @AndrejOrsula
- Add shape and ground plane assets ([1294149](https://github.com/AndrejOrsula/space_robotics_bench/commit/1294149741302d9f01f300ba1e39c6e83876a980)) by @AndrejOrsula
- Add object/scenery assets from srb_assets ([1cb3933](https://github.com/AndrejOrsula/space_robotics_bench/commit/1cb39330564285d6c0ad9087c759a12599f73106)) by @AndrejOrsula
- Add initial procedural SimForge assets ([8a42593](https://github.com/AndrejOrsula/space_robotics_bench/commit/8a42593609a0db5a7250fcbf6e094b2d6389cfca)) by @AndrejOrsula
- Add initial tools (end-effectors) ([a1b686a](https://github.com/AndrejOrsula/space_robotics_bench/commit/a1b686a17a53ed980f2fad47afa1633f4f1ab03a)) by @AndrejOrsula
- Add initial robot assets ([2669fd1](https://github.com/AndrejOrsula/space_robotics_bench/commit/2669fd16c655de6adeb6a7458aa68aa2596d1157)) by @AndrejOrsula
- Add custom Franka arm and FrankaHand tool (separate) ([594cab1](https://github.com/AndrejOrsula/space_robotics_bench/commit/594cab164e9189daea23a22252bf5596360bc92d)) by @AndrejOrsula
- Add AnyEnv/AnyEnvCfg type aliases ([c5f7098](https://github.com/AndrejOrsula/space_robotics_bench/commit/c5f7098d9255f317cedeb34bb3b62b5fd5a8e1fd)) by @AndrejOrsula
- Add GUI interface ([e5739f3](https://github.com/AndrejOrsula/space_robotics_bench/commit/e5739f3927227be31ed73e9da659fd8ec306c0d5)) by @AndrejOrsula
- Add teleop interfaces ([bf803d9](https://github.com/AndrejOrsula/space_robotics_bench/commit/bf803d9e78cd3f4c337e59330543300af5402d3d)) by @AndrejOrsula
- Add visual environment extension ([87d5c30](https://github.com/AndrejOrsula/space_robotics_bench/commit/87d5c30b91d9ec7c3b751a4183c6b724dc060d45)) by @AndrejOrsula
- Add common environment base classes ([7564e4b](https://github.com/AndrejOrsula/space_robotics_bench/commit/7564e4bd6e5617d2ec2f22f5cea9d82f6a7802f2)) by @AndrejOrsula
- Add oxidasim sampling utils ([7875e52](https://github.com/AndrejOrsula/space_robotics_bench/commit/7875e52e0d845fd6882a54fa9999637424ab11b0)) by @AndrejOrsula
- Add mobile robot action terms/groups ([7de74a9](https://github.com/AndrejOrsula/space_robotics_bench/commit/7de74a943a70f367f61952c6199b5993343fdccb)) by @AndrejOrsula
- Add task space manipulation action terms/groups ([96c3433](https://github.com/AndrejOrsula/space_robotics_bench/commit/96c3433321ef3892faa50a7475febab61c231504)) by @AndrejOrsula
- Add ParticleSpawner ([53b53d9](https://github.com/AndrejOrsula/space_robotics_bench/commit/53b53d9f8b7a193fb18fa610ea41bf33eed3540f)) by @AndrejOrsula
- Add common action terms and groups ([c6e657f](https://github.com/AndrejOrsula/space_robotics_bench/commit/c6e657fe8a45f89f7ebcbaceca9f3a897d3be525)) by @AndrejOrsula
- Add custom events ([3bd0866](https://github.com/AndrejOrsula/space_robotics_bench/commit/3bd0866903fa94895fa09cc4a2079a8653246daf)) by @AndrejOrsula
- Add custom visualization markers ([06d2ec2](https://github.com/AndrejOrsula/space_robotics_bench/commit/06d2ec260472afdb465d127cba028abdc4a66eb0)) by @AndrejOrsula
- Add custom RobotAssembler ([71cf4cb](https://github.com/AndrejOrsula/space_robotics_bench/commit/71cf4cb3b1ce811aaeabff2902030ec47a24d284)) by @AndrejOrsula
- Add extra shape spawners ([119fb84](https://github.com/AndrejOrsula/space_robotics_bench/commit/119fb84dec69270ec06882437cbd7a5d83a08372)) by @AndrejOrsula
- Add Domain enum with utils ([474fcd0](https://github.com/AndrejOrsula/space_robotics_bench/commit/474fcd0cf724d7cbbeaaed6fe800c1c3d66209ef)) by @AndrejOrsula
- Add config for RTX visuals and post-processing ([20bbc67](https://github.com/AndrejOrsula/space_robotics_bench/commit/20bbc67546e890f7f08dc69eb3fb8d6796f36bd8)) by @AndrejOrsula
- Add logging and tracing utils ([6173aa3](https://github.com/AndrejOrsula/space_robotics_bench/commit/6173aa32befdc3d615e089a6a40b930fdd9ec07a)) by @AndrejOrsula
- Add common utils ([31ba454](https://github.com/AndrejOrsula/space_robotics_bench/commit/31ba45439a833c6f6f19dbd9a20873b2bfa7ef40)) by @AndrejOrsula
- Docs: Add button for suggesting edits ([360a8bf](https://github.com/AndrejOrsula/space_robotics_bench/commit/360a8bf9f41af609dde6db40b6f2b8b7f134ccff)) by @AndrejOrsula
- Docs: Add link to Discord ([d351948](https://github.com/AndrejOrsula/space_robotics_bench/commit/d3519486d17c792ccb429dc490802c2825938e83)) by @AndrejOrsula
- Docker: Add option to install Space ROS ([a788d05](https://github.com/AndrejOrsula/space_robotics_bench/commit/a788d056e6e24400bfdd58f85ba526c13ce02be4)) by @AndrejOrsula
- CLI: Add short args and update environ for extension module update ([a30cfe0](https://github.com/AndrejOrsula/space_robotics_bench/commit/a30cfe07bc02a56d771f1ccf6363893970289839)) by @AndrejOrsula

### Changed
- CI: Build Python package with uv ([b23724e](https://github.com/AndrejOrsula/space_robotics_bench/commit/b23724ee6aa641e55f81c71959246442146da7ea)) by @AndrejOrsula
- CI: Disable llvm-cov in Rust workflow ([8f68f99](https://github.com/AndrejOrsula/space_robotics_bench/commit/8f68f995e3515e7d24b89e1ede0126b5e5b4d9de)) by @AndrejOrsula
- Pre-commit: Downgrade mdformat ([c1c8c6c](https://github.com/AndrejOrsula/space_robotics_bench/commit/c1c8c6c36911dea05084061c42e3c5eaac34f9aa)) by @AndrejOrsula
- GUI: Replace missing image ([a64b316](https://github.com/AndrejOrsula/space_robotics_bench/commit/a64b31668d1a708d550c723ce8fefa0a2c4ede26)) by @AndrejOrsula
- CI: Update Python/Rust workflows ([aa83406](https://github.com/AndrejOrsula/space_robotics_bench/commit/aa83406f50846bb83ccdcd9c4fbc014e0c72e2b2)) by @AndrejOrsula
- Update badges in README ([6fa634f](https://github.com/AndrejOrsula/space_robotics_bench/commit/6fa634ff368abdc6cd11eb81bc23c6911fb45e4f)) by @AndrejOrsula
- Patch ActionManager to improve compatibility with ActionGroup ([e882776](https://github.com/AndrejOrsula/space_robotics_bench/commit/e882776c8dc74d9d3b86efe3c44c290baf7c9f6c)) by @AndrejOrsula
- Wrap around Isaac Lab core modules ([38455a1](https://github.com/AndrejOrsula/space_robotics_bench/commit/38455a1879501ccfd12f6d0518756b82c6db71f1)) by @AndrejOrsula
- Define ActionGroup model ([d7095a6](https://github.com/AndrejOrsula/space_robotics_bench/commit/d7095a6de15102f1c5ab4ec498b4ef26effd3c02)) by @AndrejOrsula
- Define the full asset hierarchy model ([f3511a7](https://github.com/AndrejOrsula/space_robotics_bench/commit/f3511a73e1f888f7839f8e35000c55be43670ee9)) by @AndrejOrsula
- Integrate uv ([950ef53](https://github.com/AndrejOrsula/space_robotics_bench/commit/950ef53b5d7b10219e10dac69ca23a1b9e023fb4)) by @AndrejOrsula
- Update Docker setup ([866287d](https://github.com/AndrejOrsula/space_robotics_bench/commit/866287d57cf7b873af2e6b1348cb3c222832988b)) by @AndrejOrsula
- Integrate SimForge ([64c9bb6](https://github.com/AndrejOrsula/space_robotics_bench/commit/64c9bb652cf994bec9ee19cca87c6b46e82d0a95)) by @AndrejOrsula
- Update srb_assets ([b2a3757](https://github.com/AndrejOrsula/space_robotics_bench/commit/b2a3757b75933c999d68de118fbfb23b0914eed7)) by @AndrejOrsula
- Update pre-commit hooks ([a2a4d69](https://github.com/AndrejOrsula/space_robotics_bench/commit/a2a4d69749d1483095c8d353eae5dd4810edefb8)) by @AndrejOrsula
- Update copyright year to 2025 ([2c379dc](https://github.com/AndrejOrsula/space_robotics_bench/commit/2c379dc33002174acdd20947f9786a0a991e0c9a)) by @AndrejOrsula
- Update to Isaac Sim 4.5 ([3b0ff36](https://github.com/AndrejOrsula/space_robotics_bench/commit/3b0ff36484313a897d4d3c6f495993b5cb9a9792)) by @AndrejOrsula
- Update module name from space_robotics_bench to srb ([803703b](https://github.com/AndrejOrsula/space_robotics_bench/commit/803703bcfb173bc387babd547b76db6ad6ba5b33)) by @AndrejOrsula
- Build(deps): bump chrono from 0.4.39 to 0.4.40 ([2dce970](https://github.com/AndrejOrsula/space_robotics_bench/commit/2dce970e89226d7e4fd8ebf040496045626fc23b)) by @dependabot[bot] in [#46](https://github.com/AndrejOrsula/space_robotics_bench/pull/46)
- Build(deps): bump serde from 1.0.217 to 1.0.218 ([2c33aaf](https://github.com/AndrejOrsula/space_robotics_bench/commit/2c33aaf1bef0e37d3371da16dd9c558bc70fb26b)) by @dependabot[bot] in [#45](https://github.com/AndrejOrsula/space_robotics_bench/pull/45)
- Build(deps): bump AdityaGarg8/remove-unwanted-software from 4 to 5 ([c25adbf](https://github.com/AndrejOrsula/space_robotics_bench/commit/c25adbfdd389955880a7ef90960329053d70e4cf)) by @dependabot[bot] in [#44](https://github.com/AndrejOrsula/space_robotics_bench/pull/44)
- Build(deps): bump winit from 0.30.8 to 0.30.9 ([f3013a0](https://github.com/AndrejOrsula/space_robotics_bench/commit/f3013a0f22baef476bfea9a1dadede18fd49ac16)) by @dependabot[bot] in [#43](https://github.com/AndrejOrsula/space_robotics_bench/pull/43)
- Build(deps): bump serde_json from 1.0.137 to 1.0.138 ([e90c8a2](https://github.com/AndrejOrsula/space_robotics_bench/commit/e90c8a24c1d9e2653d1e67a611cb434d731fe4aa)) by @dependabot[bot] in [#38](https://github.com/AndrejOrsula/space_robotics_bench/pull/38)
- CI: Exclude GUI from llvm-cov ([eb925d7](https://github.com/AndrejOrsula/space_robotics_bench/commit/eb925d7b670f1de68e73fad43666f40f05c3dbcd)) by @AndrejOrsula
- Bump MSRV to 1.82 ([ed6a5d7](https://github.com/AndrejOrsula/space_robotics_bench/commit/ed6a5d7b09ff83643286c5694b5bb68522c3e35d)) by @AndrejOrsula
- Docker: Skip GUI build ([4dfb4de](https://github.com/AndrejOrsula/space_robotics_bench/commit/4dfb4de5d931aa6a5cb011b755199ca455e66fa2)) by @AndrejOrsula
- Build(deps): bump serde_json from 1.0.135 to 1.0.137 ([8bcc239](https://github.com/AndrejOrsula/space_robotics_bench/commit/8bcc2390caa8c53bcbc7a460a17889ca449141f7)) by @dependabot[bot] in [#36](https://github.com/AndrejOrsula/space_robotics_bench/pull/36)
- Build(deps): bump thiserror from 2.0.9 to 2.0.11 ([651785c](https://github.com/AndrejOrsula/space_robotics_bench/commit/651785ca329b2feb2d1414443fe9e1e3dd930ba2)) by @dependabot[bot] in [#34](https://github.com/AndrejOrsula/space_robotics_bench/pull/34)
- Build(deps): bump pyo3 from 0.23.3 to 0.23.4 ([422adb7](https://github.com/AndrejOrsula/space_robotics_bench/commit/422adb708bdb17b618797cac95ce75d0a2a18678)) by @dependabot[bot] in [#35](https://github.com/AndrejOrsula/space_robotics_bench/pull/35)
- Build(deps): bump serde_json from 1.0.134 to 1.0.135 ([6bc337d](https://github.com/AndrejOrsula/space_robotics_bench/commit/6bc337d237968c0b8232293c89008e10dc68a8bd)) by @dependabot[bot] in [#33](https://github.com/AndrejOrsula/space_robotics_bench/pull/33)
- Build(deps): bump home from 0.5.9 to 0.5.11 ([0f115c9](https://github.com/AndrejOrsula/space_robotics_bench/commit/0f115c99ecdb76d9f74f48253eb1ac1d72f84b6a)) by @dependabot[bot] in [#31](https://github.com/AndrejOrsula/space_robotics_bench/pull/31)
- Build(deps): bump egui from 0.29.1 to 0.30.0 ([a712228](https://github.com/AndrejOrsula/space_robotics_bench/commit/a712228628872270b179dbb5d405da59b9d037bc)) by @dependabot[bot] in [#29](https://github.com/AndrejOrsula/space_robotics_bench/pull/29)
- Build(deps): bump serde from 1.0.216 to 1.0.217 ([c68f4a1](https://github.com/AndrejOrsula/space_robotics_bench/commit/c68f4a1848eca0a6e9066a20a8779106dcbb9176)) by @dependabot[bot] in [#32](https://github.com/AndrejOrsula/space_robotics_bench/pull/32)
- Build(deps): bump sysinfo from 0.33.0 to 0.33.1 ([e21bca9](https://github.com/AndrejOrsula/space_robotics_bench/commit/e21bca9808fef309b6843c138c026e8291dc97e5)) by @dependabot[bot] in [#30](https://github.com/AndrejOrsula/space_robotics_bench/pull/30)
- Build(deps): bump egui_commonmark from 0.18.0 to 0.19.0 ([883d29a](https://github.com/AndrejOrsula/space_robotics_bench/commit/883d29a45f3b17407f1b42cf9f2441b2c4cd7390)) by @dependabot[bot] in [#27](https://github.com/AndrejOrsula/space_robotics_bench/pull/27)
- Build(deps): bump eframe from 0.29.1 to 0.30.0 ([d3151dd](https://github.com/AndrejOrsula/space_robotics_bench/commit/d3151dde127915d0f5903caa88b824f0e2538cdd)) by @dependabot[bot] in [#28](https://github.com/AndrejOrsula/space_robotics_bench/pull/28)
- Build(deps): bump egui_extras from 0.29.1 to 0.30.0 ([964a35e](https://github.com/AndrejOrsula/space_robotics_bench/commit/964a35e95da16a322d5909b9143a7a833baaa20f)) by @dependabot[bot] in [#25](https://github.com/AndrejOrsula/space_robotics_bench/pull/25)
- Build(deps): bump serde_json from 1.0.133 to 1.0.134 ([7e80f2d](https://github.com/AndrejOrsula/space_robotics_bench/commit/7e80f2d2d58c620880d59ac7789c1168ea87f18e)) by @dependabot[bot] in [#26](https://github.com/AndrejOrsula/space_robotics_bench/pull/26)
- Build(deps): bump thiserror from 2.0.7 to 2.0.9 ([fe1dfb0](https://github.com/AndrejOrsula/space_robotics_bench/commit/fe1dfb0be9a4907bb60f1a1bba0585ff7f1d0a7b)) by @dependabot[bot] in [#24](https://github.com/AndrejOrsula/space_robotics_bench/pull/24)
- Docs: Update Discord invite link ([1674cd9](https://github.com/AndrejOrsula/space_robotics_bench/commit/1674cd91fe7b5600a818f85b5f9c66598000506f)) by @AndrejOrsula
- Build(deps): bump thiserror from 2.0.6 to 2.0.7 ([c3aaa47](https://github.com/AndrejOrsula/space_robotics_bench/commit/c3aaa47c8730d64c5cb294715d6e4e93839e65c7)) by @dependabot[bot] in [#23](https://github.com/AndrejOrsula/space_robotics_bench/pull/23)
- Build(deps): bump serde from 1.0.215 to 1.0.216 ([e30ccc9](https://github.com/AndrejOrsula/space_robotics_bench/commit/e30ccc9ea478bc55bf8175a1833830243fbad5f5)) by @dependabot[bot] in [#22](https://github.com/AndrejOrsula/space_robotics_bench/pull/22)
- Build(deps): bump chrono from 0.4.38 to 0.4.39 ([18c91aa](https://github.com/AndrejOrsula/space_robotics_bench/commit/18c91aa45ff6a6a27cfafbec9f1e2007cc7423dd)) by @dependabot[bot] in [#21](https://github.com/AndrejOrsula/space_robotics_bench/pull/21)
- Build(deps): bump thiserror from 2.0.4 to 2.0.6 ([a5801fc](https://github.com/AndrejOrsula/space_robotics_bench/commit/a5801fca2e5069ef514b229132452bda3d742b85)) by @dependabot[bot] in [#20](https://github.com/AndrejOrsula/space_robotics_bench/pull/20)
- Build(deps): bump const_format from 0.2.33 to 0.2.34 ([3aa9ab2](https://github.com/AndrejOrsula/space_robotics_bench/commit/3aa9ab249242cfd96cdebd411985ef0e09ca879e)) by @dependabot[bot] in [#19](https://github.com/AndrejOrsula/space_robotics_bench/pull/19)
- Refactor: Improve organization ([12d8179](https://github.com/AndrejOrsula/space_robotics_bench/commit/12d8179ffb5546896b645c2a37f8942320a840a0)) by @AndrejOrsula
- Update dependencies (Blender 4.3.0, Isaac Lab 1.3.0, ...) ([4432d7c](https://github.com/AndrejOrsula/space_robotics_bench/commit/4432d7c0eda0097a78531fc1c1b697030fa7e3e3)) by @AndrejOrsula
- Docker: Improve handling of DDS config for ROS 2 and Space ROS ([476d4bf](https://github.com/AndrejOrsula/space_robotics_bench/commit/476d4bf845187dc86406f9023e1df2779d85733e)) by @AndrejOrsula
- Build(deps): bump sysinfo from 0.32.0 to 0.32.1 ([735c1bc](https://github.com/AndrejOrsula/space_robotics_bench/commit/735c1bc815e33e3b7a779cf4254480074c4053cb)) by @dependabot[bot] in [#17](https://github.com/AndrejOrsula/space_robotics_bench/pull/17)
- Build(deps): bump tracing-subscriber from 0.3.18 to 0.3.19 ([585fd11](https://github.com/AndrejOrsula/space_robotics_bench/commit/585fd11270a9949332bc878c9d28552fc5bdbd40)) by @dependabot[bot] in [#18](https://github.com/AndrejOrsula/space_robotics_bench/pull/18)
- Build(deps): bump tracing from 0.1.40 to 0.1.41 ([1a54067](https://github.com/AndrejOrsula/space_robotics_bench/commit/1a540670839fbdc51298070e9e601dd02bb9f974)) by @dependabot[bot] in [#16](https://github.com/AndrejOrsula/space_robotics_bench/pull/16)
- Build(deps): bump r2r from 0.9.3 to 0.9.4 ([d4e2f29](https://github.com/AndrejOrsula/space_robotics_bench/commit/d4e2f292e7efad5e192a9c0d0ad2b76cde817d08)) by @dependabot[bot] in [#15](https://github.com/AndrejOrsula/space_robotics_bench/pull/15)
- Build(deps): bump serde from 1.0.214 to 1.0.215 ([1b309d3](https://github.com/AndrejOrsula/space_robotics_bench/commit/1b309d3d8540ddccb14029287c34b9be3030b36a)) by @dependabot[bot] in [#11](https://github.com/AndrejOrsula/space_robotics_bench/pull/11)
- Build(deps): bump serde_json from 1.0.132 to 1.0.133 ([a16c951](https://github.com/AndrejOrsula/space_robotics_bench/commit/a16c951b4fc672d2d55f54ccb5ebecc360abea13)) by @dependabot[bot] in [#10](https://github.com/AndrejOrsula/space_robotics_bench/pull/10)
- Build(deps): bump codecov/codecov-action from 4 to 5 ([b5636d7](https://github.com/AndrejOrsula/space_robotics_bench/commit/b5636d7a67971605777b7a8f9b9e17162b7744bc)) by @dependabot[bot] in [#9](https://github.com/AndrejOrsula/space_robotics_bench/pull/9)
- Build(deps): bump r2r from 0.9.2 to 0.9.3 ([b37a42d](https://github.com/AndrejOrsula/space_robotics_bench/commit/b37a42d0410e142a9365a9243d89e1b51d6118d2)) by @dependabot[bot] in [#8](https://github.com/AndrejOrsula/space_robotics_bench/pull/8)
- Build(deps): bump image from 0.25.4 to 0.25.5 ([f3ab525](https://github.com/AndrejOrsula/space_robotics_bench/commit/f3ab52569c9341389133deb586e553e4f2451c57)) by @dependabot[bot] in [#7](https://github.com/AndrejOrsula/space_robotics_bench/pull/7)
- Build(deps): bump pyo3 from 0.22.5 to 0.22.6 ([4d642ed](https://github.com/AndrejOrsula/space_robotics_bench/commit/4d642ed2c52e9d714638eee8a9a25587f330865c)) by @dependabot[bot] in [#6](https://github.com/AndrejOrsula/space_robotics_bench/pull/6)
- Update rendering settings ([62dbeb6](https://github.com/AndrejOrsula/space_robotics_bench/commit/62dbeb645530c254a471fa685491c1b6a34f1019)) by @AndrejOrsula
- Build(deps): bump serde from 1.0.210 to 1.0.214 ([90ccbbe](https://github.com/AndrejOrsula/space_robotics_bench/commit/90ccbbe2f7d21d434958da26fd118c77cff64ec7)) by @dependabot[bot] in [#5](https://github.com/AndrejOrsula/space_robotics_bench/pull/5)
- Bump thiserror from 1.0.64 to 1.0.65 ([c4800c0](https://github.com/AndrejOrsula/space_robotics_bench/commit/c4800c052a31ddf0df6da0d613d49cf7d2b5fd9b)) by @dependabot[bot] in [#3](https://github.com/AndrejOrsula/space_robotics_bench/pull/3)
- Bump EmbarkStudios/cargo-deny-action from 1 to 2 ([d497810](https://github.com/AndrejOrsula/space_robotics_bench/commit/d4978109533877a87ae1cb6ce9fd15f6d5e87531)) by @dependabot[bot] in [#2](https://github.com/AndrejOrsula/space_robotics_bench/pull/2)
- Transfer script for automated procgen with Blender to `srb_assets` submodule ([137e61a](https://github.com/AndrejOrsula/space_robotics_bench/commit/137e61ad3a523c1ea877e76e338c0b4f11e28d6f)) by @AndrejOrsula
- CI: Disable docker job for Dependabot PRs ([1a70c2d](https://github.com/AndrejOrsula/space_robotics_bench/commit/1a70c2de3539f9e9d768ba448f50305e768b92be)) by @AndrejOrsula
- Docker: Use local Rust extension module if the project is mounted as a volume ([be00d09](https://github.com/AndrejOrsula/space_robotics_bench/commit/be00d093ef3bff5d747a034bd1c2e2a78c9afdd0)) by @AndrejOrsula
- Big Bang ([c8528ce](https://github.com/AndrejOrsula/space_robotics_bench/commit/c8528ce0013f7a58f300cd8e0937b88542d0b752)) by @AndrejOrsula

### Fixed
- CI: Fix Rust workflow ([2b98866](https://github.com/AndrejOrsula/space_robotics_bench/commit/2b988668c74fa81750bd849b14fbc6077f171d3f)) by @AndrejOrsula
- GUI: Fix winit initialization ([d9a3ddd](https://github.com/AndrejOrsula/space_robotics_bench/commit/d9a3ddd6b01e644f30ef966552e97e34c9e72493)) by @AndrejOrsula

### Removed
- Remove direct reference dependencies ([7fb8e73](https://github.com/AndrejOrsula/space_robotics_bench/commit/7fb8e73756d0666adf0c435087d2270b6dddb8ce)) by @AndrejOrsula
- Docs: Remove instructions about NGC Docker login ([9347214](https://github.com/AndrejOrsula/space_robotics_bench/commit/934721484e28993120dca20a0430e6426ead33fe)) by @AndrejOrsula
- Cargo-deny: Remove deprecated keys ([bd0d5da](https://github.com/AndrejOrsula/space_robotics_bench/commit/bd0d5dac3c457a3f76b3ae530ff1678a58afff7b)) by @AndrejOrsula
- Pre-commit: Remove redundant excludes ([cf6bf40](https://github.com/AndrejOrsula/space_robotics_bench/commit/cf6bf4028dac3044a0cf9864c4a7eb1bebfbf416)) by @AndrejOrsula

## New Contributors
* @AndrejOrsula made their first contribution
* @dependabot[bot] made their first contribution in [#46](https://github.com/AndrejOrsula/space_robotics_bench/pull/46)
[0.0.5]: https://github.com/AndrejOrsula/space_robotics_bench/compare/0.0.4..0.0.5
[0.0.4]: https://github.com/AndrejOrsula/space_robotics_bench/compare/0.0.3..0.0.4
[0.0.3]: https://github.com/AndrejOrsula/space_robotics_bench/compare/0.0.2..0.0.3
[0.0.2]: https://github.com/AndrejOrsula/space_robotics_bench/compare/0.0.1..0.0.2

<!-- generated by git-cliff -->
