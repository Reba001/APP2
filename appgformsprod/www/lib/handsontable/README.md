# Handsontable [![Build Status](https://travis-ci.org/handsontable/jquery-handsontable.png?branch=master)](https://travis-ci.org/handsontable/jquery-handsontable)

Handsontable is a minimalist approach to Excel-like table editor (datagrid/data grid) in HTML & jQuery. 

Requires jQuery 1.9+ or 2.0+. Runs in IE 8-11, Firefox, Chrome, Safari and Opera.

See the demos at http://handsontable.com/ or fork the example on [JSFiddle](http://jsfiddle.net/warpech/hU6Kz/).

## Usage

First, include all the dependencies. All the files that you need (apart from jQuery) are in the `dist\` directory:

```html
<script src="../lib/jquery.min.js"></script>
<script src="dist/jquery.handsontable.full.js"></script>
<link rel="stylesheet" media="screen" href="dist/jquery.handsontable.full.css">
```

Then, run `handsontable()` constructor on an empty div. After that, load some data if you wish:

```html
<div id="dataTable"></div>
<script>
  var data = [
    ["", "Kia", "Nissan", "Toyota", "Honda"],
    ["2008", 10, 11, 12, 13],
    ["2009", 20, 11, 14, 13],
    ["2010", 30, 15, 12, 13]
  ];
  $("#dataTable").handsontable({
    data: data,
    startRows: 6,
    startCols: 8
  });
</script>
```

## API Reference

Check out the new wiki pages: [Options](https://github.com/handsontable/jquery-handsontable/wiki/Options), [Methods](https://github.com/handsontable/jquery-handsontable/wiki/Methods) and [Events](https://github.com/handsontable/jquery-handsontable/wiki/Events)

## Changelog

To see the list of recent changes, see [Releases](https://github.com/handsontable/jquery-handsontable/releases).

## Questions

Please use the :new: [Handsontable Google Group](https://groups.google.com/forum/?fromgroups=#!forum/handsontable) for posting general **Questions**.

Make sure the question was not answered before in [FAQ](https://github.com/handsontable/jquery-handsontable/wiki/FAQ) or [GitHub Issues](https://github.com/handsontable/jquery-handsontable/issues)

## Reporting bugs and feature requests

Please follow this guidelines when reporting bugs and feature requests:

1. Use [GitHub Issues](https://github.com/handsontable/jquery-handsontable/issues) board to report bugs and feature requests (not my email address)
2. Please **always** write steps to reporoduce the error. That way we can focus on fixing the bug, not scratching our heads trying to reproduce it.
3. If possible, please add a JSFiddle link that shows the problem (start by forking [this fiddle](http://jsfiddle.net/warpech/hU6Kz/)). It saves me much time.
4. If you can't reproduce it on JSFiddle, please add a screenshot that shows the problem. JSFiddle is much more appreciated because it lets me start fixing straight away.

Thanks for understanding!

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md)

## Similar projects

I want to stay motivated to keep Handsontable the best possible editable datagrid on the Web. Therefore, I invite you to check out alternative projects. I would love to receive feedback if you would like to import some of their features to Handsontable.

 - [DataTables](http://datatables.net/)
 - [SlickGrid](https://github.com/mleibman/SlickGrid)
 - [jqGrid](http://www.trirand.com/blog/)
 - [jTable](http://www.jtable.org/)
 - [jui_datagrid](http://www.pontikis.net/labs/jui_datagrid/)
 - [ParamQuery](http://paramquery.com/)
 - [Ember Table](http://addepar.github.io/ember-table/)
 - [Backgrid.js](http://backgridjs.com/)
 - [dgrid](http://dojofoundation.org/packages/dgrid/)

## License

The MIT License (see the [LICENSE](https://github.com/handsontable/jquery-handsontable/blob/master/LICENSE) file for the full text)
