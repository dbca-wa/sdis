function WalkontableTable(instance, table) {
  //reference to instance
  this.instance = instance;
  this.TABLE = table;
  this.wtDom = this.instance.wtDom;
  this.wtDom.removeTextNodes(this.TABLE);

  //wtSpreader
  var parent = this.TABLE.parentNode;
  if (!parent || parent.nodeType !== 1 || !this.wtDom.hasClass(parent, 'wtHolder')) {
    var spreader = document.createElement('DIV');
    spreader.className = 'wtSpreader';
    if (parent) {
      parent.insertBefore(spreader, this.TABLE); //if TABLE is detached (e.g. in Jasmine test), it has no parentNode so we cannot attach holder to it
    }
    spreader.appendChild(this.TABLE);
  }
  this.spreader = this.TABLE.parentNode;

  //wtHider
  parent = this.spreader.parentNode;
  if (!parent || parent.nodeType !== 1 || !this.wtDom.hasClass(parent, 'wtHolder')) {
    var hider = document.createElement('DIV');
    hider.className = 'wtHider';
    if (parent) {
      parent.insertBefore(hider, this.spreader); //if TABLE is detached (e.g. in Jasmine test), it has no parentNode so we cannot attach holder to it
    }
    hider.appendChild(this.spreader);
  }
  this.hider = this.spreader.parentNode;
  this.hiderStyle = this.hider.style;
  this.hiderStyle.position = 'relative';

  //wtHolder
  parent = this.hider.parentNode;
  if (!parent || parent.nodeType !== 1 || !this.wtDom.hasClass(parent, 'wtHolder')) {
    var holder = document.createElement('DIV');
    holder.style.position = 'relative';
    holder.className = 'wtHolder';
    if (parent) {
      parent.insertBefore(holder, this.hider); //if TABLE is detached (e.g. in Jasmine test), it has no parentNode so we cannot attach holder to it
    }
    holder.appendChild(this.hider);
  }
  this.holder = this.hider.parentNode;

  //bootstrap from settings
  this.TBODY = this.TABLE.getElementsByTagName('TBODY')[0];
  if (!this.TBODY) {
    this.TBODY = document.createElement('TBODY');
    this.TABLE.appendChild(this.TBODY);
  }
  this.THEAD = this.TABLE.getElementsByTagName('THEAD')[0];
  if (!this.THEAD) {
    this.THEAD = document.createElement('THEAD');
    this.TABLE.insertBefore(this.THEAD, this.TBODY);
  }
  this.COLGROUP = this.TABLE.getElementsByTagName('COLGROUP')[0];
  if (!this.COLGROUP) {
    this.COLGROUP = document.createElement('COLGROUP');
    this.TABLE.insertBefore(this.COLGROUP, this.THEAD);
  }

  if (this.instance.getSetting('columnHeaders').length) {
    if (!this.THEAD.childNodes.length) {
      var TR = document.createElement('TR');
      this.THEAD.appendChild(TR);
    }
  }

  this.colgroupChildrenLength = this.COLGROUP.childNodes.length;
  this.theadChildrenLength = this.THEAD.firstChild ? this.THEAD.firstChild.childNodes.length : 0;
  this.tbodyChildrenLength = this.TBODY.childNodes.length;

  this.oldCellCache = new WalkontableClassNameCache();
  this.currentCellCache = new WalkontableClassNameCache();

  this.rowFilter = new WalkontableRowFilter();
  this.columnFilter = new WalkontableColumnFilter();

  this.verticalRenderReverse = false;
}

WalkontableTable.prototype.refreshHiderDimensions = function () {
  var height = this.instance.wtViewport.getWorkspaceHeight();
  var width = this.instance.wtViewport.getWorkspaceWidth();

  var spreaderStyle = this.spreader.style;

  if ((height !== Infinity || width !== Infinity) && !this.instance.getSetting('nativeScrollbars')) {
    if (height === Infinity) {
      height = this.instance.wtViewport.getWorkspaceActualHeight();
    }
    if (width === Infinity) {
      width = this.instance.wtViewport.getWorkspaceActualWidth();
    }

    this.hiderStyle.overflow = 'hidden';

    spreaderStyle.position = 'absolute';
    spreaderStyle.top = '0';
    spreaderStyle.left = '0';

    if (!this.instance.getSetting('nativeScrollbars')) {
      spreaderStyle.height = '4000px';
      spreaderStyle.width = '4000px';
    }

    if (height < 0) { //this happens with WalkontableOverlay and causes "Invalid argument" error in IE8
      height = 0;
    }

    this.hiderStyle.height = height + 'px';
    this.hiderStyle.width = width + 'px';
  }
  else {
    spreaderStyle.position = 'relative';
    spreaderStyle.width = 'auto';
    spreaderStyle.height = 'auto';
  }
};

WalkontableTable.prototype.refreshStretching = function () {
  if (this.instance.cloneSource) {
    return;
  }

  var instance = this.instance
    , stretchH = instance.getSetting('stretchH')
    , totalRows = instance.getSetting('totalRows')
    , totalColumns = instance.getSetting('totalColumns')
    , offsetColumn = instance.getSetting('offsetColumn');

  var containerWidthFn = function (cacheWidth) {
    var viewportWidth = that.instance.wtViewport.getViewportWidth(cacheWidth);
    if (viewportWidth < cacheWidth && that.instance.getSetting('nativeScrollbars')) {
      return Infinity; //disable stretching when viewport is bigger than sum of the cell widths
    }
    return viewportWidth;
  };

  var that = this;

  var columnWidthFn = function (i) {
    var source_c = that.columnFilter.visibleToSource(i);
    if (source_c < totalColumns) {
      return instance.getSetting('columnWidth', source_c);
    }
  };

  if (stretchH === 'hybrid') {
    if (offsetColumn > 0) {
      stretchH = 'last';
    }
    else {
      stretchH = 'none';
    }
  }

  var containerHeightFn = function (cacheHeight) {
    if (that.instance.getSetting('nativeScrollbars')) {
      if (that.instance.cloneOverlay instanceof WalkontableDebugOverlay) {
        return Infinity;
      }
      else {
        return 2 * that.instance.wtViewport.getViewportHeight(cacheHeight);
      }
    }
    return that.instance.wtViewport.getViewportHeight(cacheHeight);
  };

  var rowHeightFn = function (i, TD) {
    if (that.instance.getSetting('nativeScrollbars')) {
      return 20;
    }
    var source_r = that.rowFilter.visibleToSource(i);
    if (source_r < totalRows) {
      if (that.verticalRenderReverse && i === 0) {
        return that.instance.getSetting('rowHeight', source_r, TD) - 1;
      }
      else {
        return that.instance.getSetting('rowHeight', source_r, TD);
      }
    }
  };

  this.columnStrategy = new WalkontableColumnStrategy(instance, containerWidthFn, columnWidthFn, stretchH);
  this.rowStrategy = new WalkontableRowStrategy(instance, containerHeightFn, rowHeightFn);
};

WalkontableTable.prototype.adjustAvailableNodes = function () {
  var displayTds
    , rowHeaders = this.instance.getSetting('rowHeaders')
    , displayThs = rowHeaders.length
    , columnHeaders = this.instance.getSetting('columnHeaders')
    , TR
    , TD
    , c;

  //adjust COLGROUP
  while (this.colgroupChildrenLength < displayThs) {
    this.COLGROUP.appendChild(document.createElement('COL'));
    this.colgroupChildrenLength++;
  }

  this.refreshStretching(); //actually it is wrong position because it assumes rowHeader would be always 50px wide (because we measure before it is filled with text). TODO: debug
  if (this.instance.cloneSource && (this.instance.cloneOverlay instanceof WalkontableHorizontalScrollbarNative || this.instance.cloneOverlay instanceof WalkontableCornerScrollbarNative)) {
    displayTds = this.instance.getSetting('fixedColumnsLeft');
  }
  else {
    displayTds = this.columnStrategy.cellCount;
  }

  //adjust COLGROUP
  while (this.colgroupChildrenLength < displayTds + displayThs) {
    this.COLGROUP.appendChild(document.createElement('COL'));
    this.colgroupChildrenLength++;
  }
  while (this.colgroupChildrenLength > displayTds + displayThs) {
    this.COLGROUP.removeChild(this.COLGROUP.lastChild);
    this.colgroupChildrenLength--;
  }

  //adjust THEAD
  TR = this.THEAD.firstChild;
  if (columnHeaders.length) {
    if (!TR) {
      TR = document.createElement('TR');
      this.THEAD.appendChild(TR);
    }

    this.theadChildrenLength = TR.childNodes.length;
    while (this.theadChildrenLength < displayTds + displayThs) {
      TR.appendChild(document.createElement('TH'));
      this.theadChildrenLength++;
    }
    while (this.theadChildrenLength > displayTds + displayThs) {
      TR.removeChild(TR.lastChild);
      this.theadChildrenLength--;
    }
  }
  else if (TR) {
    this.wtDom.empty(TR);
  }

  //draw COLGROUP
  for (c = 0; c < this.colgroupChildrenLength; c++) {
    if (c < displayThs) {
      this.wtDom.addClass(this.COLGROUP.childNodes[c], 'rowHeader');
    }
    else {
      this.wtDom.removeClass(this.COLGROUP.childNodes[c], 'rowHeader');
    }
  }

  //draw THEAD
  if (columnHeaders.length) {
    TR = this.THEAD.firstChild;
    if (displayThs) {
      TD = TR.firstChild; //actually it is TH but let's reuse single variable
      for (c = 0; c < displayThs; c++) {
        rowHeaders[c](-displayThs + c, TD);
        TD = TD.nextSibling;
      }
    }
  }

  for (c = 0; c < displayTds; c++) {
    if (columnHeaders.length) {
      columnHeaders[0](this.columnFilter.visibleToSource(c), TR.childNodes[displayThs + c]);
    }
  }
};

WalkontableTable.prototype.adjustColumns = function (TR, desiredCount) {
  var count = TR.childNodes.length;
  while (count < desiredCount) {
    var TD = document.createElement('TD');
    TR.appendChild(TD);
    count++;
  }
  while (count > desiredCount) {
    TR.removeChild(TR.lastChild);
    count--;
  }
};

WalkontableTable.prototype.draw = function (selectionsOnly) {
  if (this.instance.getSetting('nativeScrollbars')) {
    this.verticalRenderReverse = false; //this is only supported in dragdealer mode, not in native
  }

  this.rowFilter.readSettings(this.instance);
  this.columnFilter.readSettings(this.instance);

  if (!selectionsOnly) {
    if (this.instance.getSetting('nativeScrollbars')) {
      if (this.instance.cloneSource) {
        this.tableOffset = this.instance.cloneSource.wtTable.tableOffset;
      }
      else {
        this.holderOffset = this.wtDom.offset(this.holder);
        this.tableOffset = this.wtDom.offset(this.TABLE);
        this.instance.wtScrollbars.vertical.readWindowSize();
        this.instance.wtScrollbars.horizontal.readWindowSize();
        this.instance.wtViewport.resetSettings();
      }
    }
    else {
      this.tableOffset = this.wtDom.offset(this.TABLE);
      this.instance.wtViewport.resetSettings();
    }
    this._doDraw();
  }
  else {
    this.instance.wtScrollbars && this.instance.wtScrollbars.refresh(true);
  }

  this.refreshPositions(selectionsOnly);

  if (!selectionsOnly) {
    if (this.instance.getSetting('nativeScrollbars')) {
      if (!this.instance.cloneSource) {
        this.instance.wtScrollbars.vertical.resetFixedPosition();
        this.instance.wtScrollbars.horizontal.resetFixedPosition();
        this.instance.wtScrollbars.corner.resetFixedPosition();
        this.instance.wtScrollbars.debug && this.instance.wtScrollbars.debug.resetFixedPosition();
      }
    }
  }

  this.instance.drawn = true;
  return this;
};

WalkontableTable.prototype._doDraw = function () {
  var r = 0
    , source_r
    , c
    , source_c
    , offsetRow = this.instance.getSetting('offsetRow')
    , totalRows = this.instance.getSetting('totalRows')
    , totalColumns = this.instance.getSetting('totalColumns')
    , displayTds
    , rowHeaders = this.instance.getSetting('rowHeaders')
    , displayThs = rowHeaders.length
    , TR
    , TD
    , TH
    , adjusted = false
    , workspaceWidth
    , mustBeInViewport
    , res;

  if (this.verticalRenderReverse) {
    mustBeInViewport = offsetRow;
  }

  var noPartial = false;
  if (this.verticalRenderReverse) {
    if (offsetRow === totalRows - this.rowFilter.fixedCount - 1) {
      noPartial = true;
    }
    else {
      this.instance.update('offsetRow', offsetRow + 1); //if we are scrolling reverse
      this.rowFilter.readSettings(this.instance);
    }
  }

  if (this.instance.cloneSource) {
    this.columnStrategy = this.instance.cloneSource.wtTable.columnStrategy;
    this.rowStrategy = this.instance.cloneSource.wtTable.rowStrategy;
  }

  //draw TBODY
  if (totalColumns > 0) {
    source_r = this.rowFilter.visibleToSource(r);

    var fixedRowsTop = this.instance.getSetting('fixedRowsTop');
    var cloneLimit;
    if (this.instance.cloneSource) { //must be run after adjustAvailableNodes because otherwise this.rowStrategy is not yet defined
      if (this.instance.cloneOverlay instanceof WalkontableVerticalScrollbarNative || this.instance.cloneOverlay instanceof WalkontableCornerScrollbarNative) {
        cloneLimit = fixedRowsTop;
      }
      else if (this.instance.cloneOverlay instanceof WalkontableHorizontalScrollbarNative) {
        cloneLimit = this.rowStrategy.countVisible();
      }
      //else if WalkontableDebugOverlay do nothing. No cloneLimit means render ALL rows
    }

    this.adjustAvailableNodes();
    adjusted = true;

    if (this.instance.cloneSource && (this.instance.cloneOverlay instanceof WalkontableHorizontalScrollbarNative || this.instance.cloneOverlay instanceof WalkontableCornerScrollbarNative)) {
      displayTds = this.instance.getSetting('fixedColumnsLeft');
    }
    else {
      displayTds = this.columnStrategy.cellCount;
    }

    if (!this.instance.cloneSource) {
      workspaceWidth = this.instance.wtViewport.getWorkspaceWidth();
      this.columnStrategy.stretch();
    }

    for (c = 0; c < displayTds; c++) {
      this.COLGROUP.childNodes[c + displayThs].style.width = this.columnStrategy.getSize(c) + 'px';
    }

    while (source_r < totalRows && source_r >= 0) {
      if (r > 1000) {
        throw new Error('Security brake: Too much TRs. Please define height for your table, which will enforce scrollbars.');
      }

      if (cloneLimit !== void 0 && r === cloneLimit) {
        break; //we have as much rows as needed for this clone
      }

      if (r >= this.tbodyChildrenLength || (this.verticalRenderReverse && r >= this.rowFilter.fixedCount)) {
        TR = document.createElement('TR');
        for (c = 0; c < displayThs; c++) {
          TR.appendChild(document.createElement('TH'));
        }
        if (this.verticalRenderReverse && r >= this.rowFilter.fixedCount) {
          this.TBODY.insertBefore(TR, this.TBODY.childNodes[this.rowFilter.fixedCount] || this.TBODY.firstChild);
        }
        else {
          this.TBODY.appendChild(TR);
        }
        this.tbodyChildrenLength++;
      }
      else if (r === 0) {
        TR = this.TBODY.firstChild;
      }
      else {
        TR = TR.nextSibling; //http://jsperf.com/nextsibling-vs-indexed-childnodes
      }

      //TH
      TH = TR.firstChild;
      for (c = 0; c < displayThs; c++) {

        //If the number of row headers increased we need to replace TD with TH
        if (TH.nodeName == 'TD') {
          TD = TH;
          TH = document.createElement('TH');
          TR.insertBefore(TH, TD);
          TR.removeChild(TD);
        }

        rowHeaders[c](source_r, TH); //actually TH
        TH = TH.nextSibling; //http://jsperf.com/nextsibling-vs-indexed-childnodes
      }

      this.adjustColumns(TR, displayTds + displayThs);

      for (c = 0; c < displayTds; c++) {
        source_c = this.columnFilter.visibleToSource(c);
        if (c === 0) {
          TD = TR.childNodes[this.columnFilter.sourceColumnToVisibleRowHeadedColumn(source_c)];
        }
        else {
          TD = TD.nextSibling; //http://jsperf.com/nextsibling-vs-indexed-childnodes
        }

        //If the number of headers has been reduced, we need to replace excess TH with TD
        if (TD.nodeName == 'TH') {
          TH = TD;
          TD = document.createElement('TD');
          TR.insertBefore(TD, TH);
          TR.removeChild(TH);
        }

        TD.className = '';
        TD.removeAttribute('style');
        this.instance.getSetting('cellRenderer', source_r, source_c, TD);
      }

      offsetRow = this.instance.getSetting('offsetRow'); //refresh the value

      //after last column is rendered, check if last cell is fully displayed
      if (this.verticalRenderReverse && noPartial) {
        if (-this.wtDom.outerHeight(TR.firstChild) < this.rowStrategy.remainingSize) {
          this.TBODY.removeChild(TR);
          this.instance.update('offsetRow', offsetRow + 1);
          this.tbodyChildrenLength--;
          this.rowFilter.readSettings(this.instance);
          break;

        }
        else if (!this.instance.cloneSource) {
          res = this.rowStrategy.add(r, TD, this.verticalRenderReverse);
          if (res === false) {
            this.rowStrategy.removeOutstanding();
          }
        }
      }
      else if (!this.instance.cloneSource) {
        res = this.rowStrategy.add(r, TD, this.verticalRenderReverse);

        if (res === false) {
          if (!this.instance.getSetting('nativeScrollbars')) {
            this.rowStrategy.removeOutstanding();
          }
        }

        if (this.rowStrategy.isLastIncomplete()) {
          if (this.verticalRenderReverse && !this.isRowInViewport(mustBeInViewport)) {
            //we failed because one of the cells was by far too large. Recover by rendering from top
            this.verticalRenderReverse = false;
            this.instance.update('offsetRow', mustBeInViewport);
            this.draw();
            return;
          }
          break;
        }
      }

      if (this.instance.getSetting('nativeScrollbars')) {
        if (this.instance.cloneSource) {
          TR.style.height = this.instance.getSetting('rowHeight', source_r) + 'px'; //if I have 2 fixed columns with one-line content and the 3rd column has a multiline content, this is the way to make sure that the overlay will has same row height
        }
        else {
          this.instance.getSetting('rowHeight', source_r, TD); //this trick saves rowHeight in rowHeightCache. It is then read in WalkontableVerticalScrollbarNative.prototype.sumCellSizes and reset in Walkontable constructor
        }
      }

      if (this.verticalRenderReverse && r >= this.rowFilter.fixedCount) {
        if (offsetRow === 0) {
          break;
        }
        this.instance.update('offsetRow', offsetRow - 1);
        this.rowFilter.readSettings(this.instance);
      }
      else {
        r++;
      }

      source_r = this.rowFilter.visibleToSource(r);
    }
  }

  if (!adjusted) {
    this.adjustAvailableNodes();
  }

  if (!(this.instance.cloneOverlay instanceof WalkontableDebugOverlay)) {
    r = this.rowStrategy.countVisible();
    while (this.tbodyChildrenLength > r) {
      this.TBODY.removeChild(this.TBODY.lastChild);
      this.tbodyChildrenLength--;
    }
  }

  this.instance.wtScrollbars && this.instance.wtScrollbars.refresh(false);

  if (!this.instance.cloneSource) {
    if (workspaceWidth !== this.instance.wtViewport.getWorkspaceWidth()) {
      //workspace width changed though to shown/hidden vertical scrollbar. Let's reapply stretching
      this.columnStrategy.stretch();
      for (c = 0; c < this.columnStrategy.cellCount; c++) {
        this.COLGROUP.childNodes[c + displayThs].style.width = this.columnStrategy.getSize(c) + 'px';
      }
    }
  }

  this.verticalRenderReverse = false;
};

WalkontableTable.prototype.refreshPositions = function (selectionsOnly) {
  this.refreshHiderDimensions();
  this.refreshSelections(selectionsOnly);
};

WalkontableTable.prototype.refreshSelections = function (selectionsOnly) {
  var vr
    , r
    , vc
    , c
    , s
    , slen
    , classNames = []
    , visibleRows = this.rowStrategy.countVisible()
    , visibleColumns = this.columnStrategy.countVisible();

  this.oldCellCache = this.currentCellCache;
  this.currentCellCache = new WalkontableClassNameCache();

  if (this.instance.selections) {
    for (r in this.instance.selections) {
      if (this.instance.selections.hasOwnProperty(r)) {
        this.instance.selections[r].draw();
        if (this.instance.selections[r].settings.className) {
          classNames.push(this.instance.selections[r].settings.className);
        }
        if (this.instance.selections[r].settings.highlightRowClassName) {
          classNames.push(this.instance.selections[r].settings.highlightRowClassName);
        }
        if (this.instance.selections[r].settings.highlightColumnClassName) {
          classNames.push(this.instance.selections[r].settings.highlightColumnClassName);
        }
      }
    }
  }

  slen = classNames.length;

  for (vr = 0; vr < visibleRows; vr++) {
    for (vc = 0; vc < visibleColumns; vc++) {
      r = this.rowFilter.visibleToSource(vr);
      c = this.columnFilter.visibleToSource(vc);
      for (s = 0; s < slen; s++) {
        if (this.currentCellCache.test(vr, vc, classNames[s])) {
          this.wtDom.addClass(this.getCell([r, c]), classNames[s]);
        }
        else if (selectionsOnly && this.oldCellCache.test(vr, vc, classNames[s])) {
          this.wtDom.removeClass(this.getCell([r, c]), classNames[s]);
        }
      }
    }
  }
};

/**
 * getCell
 * @param {Array} coords
 * @return {Object} HTMLElement on success or {Number} one of the exit codes on error:
 *  -1 row before viewport
 *  -2 row after viewport
 *  -3 column before viewport
 *  -4 column after viewport
 *
 */
WalkontableTable.prototype.getCell = function (coords) {
  if (this.isRowBeforeViewport(coords[0])) {
    return -1; //row before viewport
  }
  else if (this.isRowAfterViewport(coords[0])) {
    return -2; //row after viewport
  }
  else {
    if (this.isColumnBeforeViewport(coords[1])) {
      return -3; //column before viewport
    }
    else if (this.isColumnAfterViewport(coords[1])) {
      return -4; //column after viewport
    }
    else {
      return this.TBODY.childNodes[this.rowFilter.sourceToVisible(coords[0])].childNodes[this.columnFilter.sourceColumnToVisibleRowHeadedColumn(coords[1])];
    }
  }
};

WalkontableTable.prototype.getCoords = function (TD) {
  return [
    this.rowFilter.visibleToSource(this.wtDom.index(TD.parentNode)),
    this.columnFilter.visibleRowHeadedColumnToSourceColumn(TD.cellIndex)
  ];
};

//returns -1 if no row is visible
WalkontableTable.prototype.getLastVisibleRow = function () {
  return this.rowFilter.visibleToSource(this.rowStrategy.cellCount - 1);
};

//returns -1 if no column is visible
WalkontableTable.prototype.getLastVisibleColumn = function () {
  return this.columnFilter.visibleToSource(this.columnStrategy.cellCount - 1);
};

WalkontableTable.prototype.isRowBeforeViewport = function (r) {
  return (this.rowFilter.sourceToVisible(r) < this.rowFilter.fixedCount && r >= this.rowFilter.fixedCount);
};

WalkontableTable.prototype.isRowAfterViewport = function (r) {
  return (r > this.getLastVisibleRow());
};

WalkontableTable.prototype.isColumnBeforeViewport = function (c) {
  return (this.columnFilter.sourceToVisible(c) < this.columnFilter.fixedCount && c >= this.columnFilter.fixedCount);
};

WalkontableTable.prototype.isColumnAfterViewport = function (c) {
  return (c > this.getLastVisibleColumn());
};

WalkontableTable.prototype.isRowInViewport = function (r) {
  return (!this.isRowBeforeViewport(r) && !this.isRowAfterViewport(r));
};

WalkontableTable.prototype.isColumnInViewport = function (c) {
  return (!this.isColumnBeforeViewport(c) && !this.isColumnAfterViewport(c));
};

WalkontableTable.prototype.isLastRowFullyVisible = function () {
  return (this.getLastVisibleRow() === this.instance.getSetting('totalRows') - 1 && !this.rowStrategy.isLastIncomplete());
};

WalkontableTable.prototype.isLastColumnFullyVisible = function () {
  return (this.getLastVisibleColumn() === this.instance.getSetting('totalColumns') - 1 && !this.columnStrategy.isLastIncomplete());
};
