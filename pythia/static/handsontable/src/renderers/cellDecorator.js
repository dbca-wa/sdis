(function (Handsontable) {
  'use strict';

  /*
    Adds appropriate CSS class to table cell, based on cellProperties
   */
  Handsontable.renderers.cellDecorator = function (instance, TD, row, col, prop, value, cellProperties) {
    if (cellProperties.readOnly) {
      instance.view.wt.wtDom.addClass(TD, cellProperties.readOnlyCellClassName);
    }

    if (cellProperties.valid === false && cellProperties.invalidCellClassName) {
      instance.view.wt.wtDom.addClass(TD, cellProperties.invalidCellClassName);
    }

    if (!value && cellProperties.placeholder) {
      instance.view.wt.wtDom.addClass(TD, cellProperties.placeholderCellClassName);
    }
  }

})(Handsontable);