function parseDatacolumn(HANDSONTABLE, HOTCOLUMN) {
  var obj = {}
    , attrName
    , i
    , ilen
    , val;

  for (i = 0, ilen = publicProperties.length; i < ilen; i++) {
    attrName = publicProperties[i];
    if (attrName === 'data') {
      attrName = 'value';
    }
    else if (attrName === 'title') {
      attrName = 'header';
    }

    if (HOTCOLUMN[attrName] === null) {
      continue; //default value
    }
    else if (HOTCOLUMN[attrName] !== void 0 && HOTCOLUMN[attrName] !== "") {
      val = HOTCOLUMN[attrName];
    }
    else {
      val = HOTCOLUMN.getAttribute(attrName); //Dec 3, 2013 - Polymer returns empty string for node properties such as HOTCOLUMN.width
    }

    if (val !== void 0 && val !== HANDSONTABLE[attrName]) {
      obj[publicProperties[i]] = readOption(HOTCOLUMN, attrName, val);
    }
  }

  var inner_HANDSONTABLE = HOTCOLUMN.getElementsByTagName('handsontable-table');
  if (inner_HANDSONTABLE.length) {
    obj.handsontable = parseHandsontable(inner_HANDSONTABLE[0]);
  }

  return obj;
}

function getModel(HANDSONTABLE) {
  if (HANDSONTABLE.templateInstance) {
    return HANDSONTABLE.templateInstance.model;
  }
  else {
    return window;
  }
}

function getModelPath(HANDSONTABLE, path) {
  if (typeof path === 'object' || typeof path === 'function') { //happens in Polymer when assigning as datarows="{{ model.subpage.people }}" or settings="{{ model.subpage.settings }}
    return path;
  }
  var model = getModel(HANDSONTABLE);
  var expression = 'with(model) { ' + path + ';}';
  var obj = eval(expression);
  return (obj);
}

function parseDatacolumns(HANDSONTABLE) {
  var columns = []
    , i
    , ilen;

  for (i = 0, ilen = HANDSONTABLE.childNodes.length; i < ilen; i++) {
    if (HANDSONTABLE.childNodes[i].nodeName === 'HANDSONTABLE-COLUMN') {
      columns.push(parseDatacolumn(HANDSONTABLE, HANDSONTABLE.childNodes[i]));
    }
  }

  return columns;
}

function readOption(HANDSONTABLE, key, value) {
  if (key === 'datarows') {
    return getModelPath(HANDSONTABLE, value);
  }
  else if (key === 'renderer') {
    return getModelPath(HANDSONTABLE, value);
  }
  else if (key === 'source') {
    return getModelPath(HANDSONTABLE, value);
  }
  else if (key === 'afterOnCellMouseOver') {
    return getModelPath(HANDSONTABLE, value);
  }
  else if (publicHooks.indexOf(key) > -1) {
    return getModelPath(HANDSONTABLE, value);
  }
  else {
    return readBool(value);
  }
}

function parseHandsontable(HANDSONTABLE) {
  var columns = parseDatacolumns(HANDSONTABLE);
  var options = webComponentDefaults();
  var attrName, i, ilen;

  for (i = 0, ilen = publicProperties.length; i < ilen; i++) {
    attrName = publicProperties[i];
    if (attrName === 'data') {
      attrName = 'datarows';
    }
    options[publicProperties[i]] = readOption(HANDSONTABLE, attrName, HANDSONTABLE[attrName]);
  }

  if (HANDSONTABLE.settings) {
    var settingsAttr = getModelPath(HANDSONTABLE, HANDSONTABLE.settings);
    for (i in settingsAttr) {
      if (settingsAttr.hasOwnProperty(i)) {
        options[i] = settingsAttr[i];
      }
    }
  }

  if (columns.length) {
    options.columns = columns;
  }

  return options;
}

var publicMethods = ['updateSettings', 'loadData', 'render', 'setDataAtCell', 'setDataAtRowProp', 'getDataAtCell', 'getDataAtRowProp', 'countRows', 'countCols', 'rowOffset', 'colOffset', 'countVisibleRows', 'countVisibleCols', 'clear', 'clearUndo', 'getData', 'alter', 'getCell', 'getCellMeta', 'selectCell', 'deselectCell', 'getSelected', 'destroyEditor', 'getRowHeader', 'getColHeader', 'destroy', 'isUndoAvailable', 'isRedoAvailable', 'undo', 'redo', 'countEmptyRows', 'countEmptyCols', /*'isEmptyRow', 'isEmptyCol', -- those are also publicProperties*/ 'parseSettingsFromDOM', 'addHook', 'addHookOnce', 'getValue', 'getInstance', 'getSettings'];
var publicHooks = Object.keys(Handsontable.PluginHooks.hooks);
var publicProperties = Object.keys(Handsontable.DefaultSettings.prototype);
publicProperties.push('settings', 'source', 'title', 'checkedTemplate', 'uncheckedTemplate', 'renderer'); //properties not mentioned in DefaultSettings

publicProperties = publicProperties.concat(publicHooks);

function webComponentDefaults() {
  return {
    observeChanges: true
  }
}

var wcDefaults = webComponentDefaults();

var publish = {
};

publicMethods.forEach(function (hot_method) {
  publish[hot_method] = function () {
    return this.instance[hot_method].apply(this.instance, arguments);
  }
});

publicProperties.forEach(function (hot_prop) {
  if (!publish[hot_prop]) {
    var wc_prop = hot_prop;

    if (hot_prop === 'data') {
      wc_prop = 'datarows';
    }
    else if (hot_prop === 'title') {
      //rename 'title' attribute to 'header' because 'title' was causing problems (https://groups.google.com/forum/#!topic/polymer-dev/RMMsV-D4HVw)
      wc_prop = 'header';
    }

    var val = wcDefaults[hot_prop] === void 0 ? Handsontable.DefaultSettings.prototype[hot_prop] : wcDefaults[hot_prop];

    if (val === void 0) {
      publish[wc_prop] = null; //Polymer does not like undefined
    }
    else if (hot_prop === 'observeChanges') {
      publish[wc_prop] = true; //on by default
    }
    else {
      publish[wc_prop] = val;
    }

    publish[wc_prop + 'Changed'] = function () {
      if (!this.instance) {
        return; //attribute changed callback called before enteredView
      }

      if (wc_prop === 'settings') {
        var settings = getModelPath(this, this[wc_prop]);
        this.updateSettings(settings);
        return;
      }

      var update = {};
      update[hot_prop] = readOption(this, wc_prop, this[wc_prop]);
      this.updateSettings(update);
    }
  }
});

function readBool(val) {
  if (val === void 0 || val === "false") {
    return false;
  }
  else if (val === "" || val === "true") {
    return true;
  }
  return val;
}

Polymer('handsontable-table', {
  instance: null,
  enteredView: function () {
    this.shadowRoot.applyAuthorStyles = true; //only way I know to let override Shadow DOM styles (just define ".handsontable td" in page stylesheet)
    //TODO applyAuthorStyles was removed from Shadow DOM spec and Canary. Investigate if/when the above line can be removed. See: https://groups.google.com/d/topic/polymer-dev/Kig_r-7xuX4/discussion

    jQuery(this.$.htContainer).handsontable(parseHandsontable(this));
    this.instance = jQuery(this.$.htContainer).data('handsontable');
  },
  onMutation: function () {
    if (this === window) {
      //it is a bug in Polymer or Chrome as of Nov 29, 2013
      return;
    }
    if (!this.instance) {
      //happens in Handsontable WC demo page in Chrome 33-dev
      return;
    }
    var columns = parseDatacolumns(this);
    if (columns.length) {
      this.updateSettings({columns: columns});
    }
  },
  publish: publish
});