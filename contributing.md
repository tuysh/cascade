# Contributing!

First off, thanks for taking the time to contribute! <3

All types of contributions are encouraged and welcome. 💜
Though please make sure to read through the following guidelines before making your contribution. It will make it a lot easier for us maintainers and smooth out the experience for all involved.
Besides the creation and maintenance of ports we appreciate all sorts of code and non-code contributions. These include but are not limited to:

- Typo fixes
- Documentation improvements
- Pull request reviews
- Feature requests
- Opinions & suggestions

&nbsp;

## ✔️ Guidelines

The following is a set of guidelines for contributing to this project. Use your best judgment, and feel free to propose changes to this document in a pull request.

- PRs go to `main`. Keep them focused, with commit messages in the conventional
  commits style used by the history (`fix(tabs): …`, `feat(nav-bar): …`).
- Use the `.editorconfig` file at the root of this project in your editor, so as to
  "maintain consistent coding styles" ([EditorConfig](https://editorconfig.org/)).
- A new option is a `--uc-*` custom property declared, with a comment, in both
  `cascade-config.css` and `cascade-config-mouse.css`, plus a `:where(:root)` default
  in the include that reads it, so older config files keep working.
- Colours come from the palette (`--uc-*-colour`); never hard-code one in an include.
- `userChrome.css` is a user stylesheet: a declaration without `!important` loses to
  any of Firefox's own declarations for the same property, whatever its specificity.
- Test with the current Firefox release: Nova on and off (`browser.nova.enabled`),
  compact / normal / touch density, vertical tabs (`sidebar.verticalTabs`), light and
  dark, and both config files. Add before / after screenshots to the PR.
  `tools/firefox-harness/` can take them for you in the real browser.

> When contributing to this project, you must agree that you have authored 100% of the content, (or) that you have the necessary rights to the content and that the content you contribute may be provided under the [projects MIT license](LICENSE).

&nbsp;

## 💡 Recommendations

- Create a topic branch on your fork for your specific PR.
- If it's your first time contributing to a project then read [About pull requests](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) on Github's docs.

&nbsp;
