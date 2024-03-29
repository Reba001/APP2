# Contributing to Handsontable

Your contributions to the project are very welcome. If you would like to fix a bug or propose a new feature, you can submit a Pull Request.

To help us merge your Pull Request, please make sure you follow these points:

1. Please make your fix on a separate branch. This makes merging much easier.
2. Do not edit files `jquery.handsontable.js`, `jquery.handsontable.css`, `jquery.handsontable.full.js`, `jquery.handsontable.full.css`. Instead, try to edit files inside the `src/` directory and then use `grunt` to make a build. More information about this on wiki page [Building](https://github.com/warpech/jquery-handsontable/wiki/Building).
3. Very important: For any change that you make, **please try to also add a test case(s)** in `tests/jasmine/spec/` or `src/3rdparty/walkontable/test/jasmine/spec/`. This helps us understand the issue and make sure that it will stay fixed forever. See [Testing](https://github.com/warpech/jquery-handsontable/wiki/Testing)
4. Describe the problem in the Pull Request description (of course you would do it, why do I mention that?)

Thank you for your commitment!

## Team rules

The Handsontable team utilizes Git-Flow. See [How we use Git-Flow](https://github.com/warpech/jquery-handsontable/wiki/How-we-use-Git-Flow)
