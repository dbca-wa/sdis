function WalkontableViewport(instance) {
  this.instance = instance;
  this.resetSettings();

  if (this.instance.getSetting('nativeScrollbars')) {
    var that = this;
    $(window).on('resize', function () {
      that.clientHeight = that.getWorkspaceHeight();
    });
  }
}

/*WalkontableViewport.prototype.isInSightVertical = function () {
  //is table outside viewport bottom edge
  if (tableTop > windowHeight + scrollTop) {
    return -1;
  }

  //is table outside viewport top edge
  else if (scrollTop > tableTop + tableFakeHeight) {
    return -2;
  }

  //table is in viewport but how much exactly?
  else {

  }
};*/

//used by scrollbar
WalkontableViewport.prototype.getWorkspaceHeight = function (proposedHeight) {
  if (this.instance.getSetting('nativeScrollbars')) {
    return this.instance.wtScrollbars.vertical.windowSize;
  }

  var height = this.instance.getSetting('height');

  if (height === Infinity || height === void 0 || height === null || height < 1) {
    if (this.instance.wtScrollbars.vertical instanceof WalkontableOverlay) {
      height = this.instance.wtScrollbars.vertical.availableSize();
    }
    else {
      height = Infinity;
    }
  }

  if (height !== Infinity) {
    if (proposedHeight >= height) {
      height -= this.instance.getSetting('scrollbarHeight');
    }
    else if (this.instance.wtScrollbars.horizontal.visible) {
      height -= this.instance.getSetting('scrollbarHeight');
    }
  }

  return height;
};

WalkontableViewport.prototype.getWorkspaceWidth = function (proposedWidth) {
  var width = this.instance.getSetting('width');

  if (width === Infinity || width === void 0 || width === null || width < 1) {
    if (this.instance.wtScrollbars.horizontal instanceof WalkontableOverlay) {
      width = this.instance.wtScrollbars.horizontal.availableSize();
    }
    else {
      width = Infinity;
    }
  }

  if (width !== Infinity) {
    if (proposedWidth >= width) {
      width -= this.instance.getSetting('scrollbarWidth');
    }
    else if (this.instance.wtScrollbars.vertical.visible) {
      width -= this.instance.getSetting('scrollbarWidth');
    }
  }
  return width;
};

WalkontableViewport.prototype.getWorkspaceActualHeight = function () {
  return this.instance.wtDom.outerHeight(this.instance.wtTable.TABLE);
};

WalkontableViewport.prototype.getWorkspaceActualWidth = function () {
  return this.instance.wtDom.outerWidth(this.instance.wtTable.TABLE) || this.instance.wtDom.outerWidth(this.instance.wtTable.TBODY) || this.instance.wtDom.outerWidth(this.instance.wtTable.THEAD); //IE8 reports 0 as <table> offsetWidth;
};

WalkontableViewport.prototype.getColumnHeaderHeight = function () {
  if (isNaN(this.columnHeaderHeight)) {
    var cellOffset = this.instance.wtDom.offset(this.instance.wtTable.TBODY)
      , tableOffset = this.instance.wtTable.tableOffset;
    this.columnHeaderHeight = cellOffset.top - tableOffset.top;
  }
  return this.columnHeaderHeight;
};

WalkontableViewport.prototype.getViewportHeight = function (proposedHeight) {
  var containerHeight = this.getWorkspaceHeight(proposedHeight);

  if (containerHeight === Infinity) {
    return containerHeight;
  }

  var columnHeaderHeight = this.getColumnHeaderHeight();
  if (columnHeaderHeight > 0) {
    return containerHeight - columnHeaderHeight;
  }
  else {
    return containerHeight;
  }
};

WalkontableViewport.prototype.getRowHeaderWidth = function () {
  if (this.instance.cloneSource) {
    return this.instance.cloneSource.wtViewport.getRowHeaderWidth();
  }
  if (isNaN(this.rowHeaderWidth)) {
    var rowHeaders = this.instance.getSetting('rowHeaders');
    if (rowHeaders.length) {
      var TH = this.instance.wtTable.TABLE.querySelector('TH');
      this.rowHeaderWidth = 0;
      for (var i = 0, ilen = rowHeaders.length; i < ilen; i++) {
        if (TH) {
          this.rowHeaderWidth += this.instance.wtDom.outerWidth(TH);
          TH = TH.nextSibling;
        }
        else {
          this.rowHeaderWidth += 50; //yes this is a cheat but it worked like that before, just taking assumption from CSS instead of measuring. TODO: proper fix
        }
      }
    }
    else {
      this.rowHeaderWidth = 0;
    }
  }
  return this.rowHeaderWidth;
};

WalkontableViewport.prototype.getViewportWidth = function (proposedWidth) {
  var containerWidth = this.getWorkspaceWidth(proposedWidth);

  if (containerWidth === Infinity) {
    return containerWidth;
  }

  var rowHeaderWidth = this.getRowHeaderWidth();
  if (rowHeaderWidth > 0) {
    return containerWidth - rowHeaderWidth;
  }
  else {
    return containerWidth;
  }
};

WalkontableViewport.prototype.resetSettings = function () {
  this.rowHeaderWidth = NaN;
  this.columnHeaderHeight = NaN;
};