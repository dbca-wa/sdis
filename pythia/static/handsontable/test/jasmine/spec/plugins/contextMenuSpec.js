describe('ContextMenu', function () {
  var id = 'testContainer';

  beforeEach(function () {
    this.$container = $('<div id="' + id + '"></div>').appendTo('body');
  });

  afterEach(function () {
    if (this.$container) {
      destroy();
      this.$container.remove();
    }
  });

  describe("menu opening", function () {
    it("should open menu after right click on table cell", function () {
      var hot = handsontable({
        contextMenu: true
      });

      expect(hot.contextMenu).toBeDefined();
      expect($(hot.contextMenu.menu).is(':visible')).toBe(false);

      contextMenu();

      expect($(hot.contextMenu.menu).is(':visible')).toBe(true);


    });

    it("should open menu after right click active cell border", function () {
      var hot = handsontable({
        contextMenu: true
      });

      expect(hot.contextMenu).toBeDefined();
      expect($(hot.contextMenu.menu).is(':visible')).toBe(false);

      selectCell(0, 0);
      var cellOffset = $(getCell(0, 0)).offset();

      var event = $.Event('contextmenu', {
        pageX: cellOffset.left,
        pageY: cellOffset.top
      });

      this.$container.find('.wtBorder.current:eq(0)').trigger(event);

      expect($(hot.contextMenu.menu).is(':visible')).toBe(true);


    });
  });

  describe('menu closing', function () {
    it("should close menu after click", function () {
      var hot = handsontable({
        contextMenu: true
      });

      contextMenu();

      expect($(hot.contextMenu.menu).is(':visible')).toBe(true);

      mouseDown(this.$container);

      expect($(hot.contextMenu.menu).is(':visible')).toBe(false);

    });
  });

  describe("menu disabled", function () {

    it("should not open menu after right click", function () {
      var hot = handsontable({
        contextMenu: true
      });

      hot.contextMenu.disable();

      expect($(hot.contextMenu.menu).is(':visible')).toBe(false);

      contextMenu();

      expect($(hot.contextMenu.menu).is(':visible')).toBe(false);

    });

    it("should not create context menu if it's disabled in constructor options", function () {
      var hot = handsontable({
        contextMenu: false
      });

      expect(hot.contextMenu).toBeUndefined();

    });

    it("should reenable menu", function () {
      var hot = handsontable({
        contextMenu: true
      });

      hot.contextMenu.disable();

      expect($(hot.contextMenu.menu).is(':visible')).toBe(false);

      contextMenu();

      expect($(hot.contextMenu.menu).is(':visible')).toBe(false);

      hot.contextMenu.enable();

      contextMenu();

      expect($(hot.contextMenu.menu).is(':visible')).toBe(true);
    });

    it("should reenable menu with updateSettings when it was disabled in constructor", function () {
      var hot = handsontable({
        contextMenu: false
      });

      expect(hot.contextMenu).toBeUndefined();

      updateSettings({
        contextMenu: true
      });

      expect(hot.contextMenu).toBeDefined();

      expect($(hot.contextMenu.menu).is(':visible')).toBe(false);

      contextMenu();

      expect($(hot.contextMenu.menu).is(':visible')).toBe(true);
    });

    it("should disable menu with updateSettings when it was enabled in constructor", function () {
      var hot = handsontable({
        contextMenu: true
      });

      expect(hot.contextMenu).toBeDefined();
      expect($('.htContextMenu').length).toEqual(1);

      updateSettings({
        contextMenu: false
      });

      expect(hot.contextMenu).toBeUndefined();
      expect($('.htContextMenu').length).toEqual(0);
    });

    it('should work properly (remove row) after destroy and new init', function () {
      var test = function () {
        var hot = handsontable({
          startRows: 5,
          contextMenu: ['remove_row']
        });
        selectCell(0, 0);
        contextMenu();
        $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(0).trigger('mousedown');
        expect(getData().length).toEqual(4);
      };
      test();

      destroy();

      test();
    });

  });

  describe("menu destroy", function () {

    it("should destroy menu together with handsontable", function () {
      var hot = handsontable({
        contextMenu: true
      });

      expect($('.htContextMenu').length).toEqual(1);

      destroy();

      expect($('.htContextMenu').length).toEqual(0);

    });

    it("should close context menu when HOT is being destroyed", function () {
      var hot = handsontable({
        contextMenu: true
      });

      contextMenu();

      expect($(hot.contextMenu.menu).is(':visible')).toBe(true);

      destroy();

      expect($(hot.contextMenu.menu).is(':visible')).toBe(false);

    });

  });

  describe("default context menu actions", function () {

    it("should display the default set of actions", function () {
      var hot = handsontable({
        contextMenu: true
      });

      contextMenu();

      var items = $('.htContextMenu tbody td');
      var actions = items.not('.htSeparator');
      var separators = items.filter('.htSeparator');

      expect(actions.length).toEqual(8);
      expect(separators.length).toEqual(3);

      expect(actions.text()).toEqual([
        'Insert row above',
        'Insert row below',
        'Insert column on the left',
        'Insert column on the right',
        'Remove row',
        'Remove column',
        'Undo',
        'Redo'
      ].join(''));

    });

    it("should insert row above selection", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      var afterCreateRowCallback = jasmine.createSpy('afterCreateRowCallback');
      hot.addHook('afterCreateRow', afterCreateRowCallback);

      expect(countRows()).toEqual(4);

      selectCell(1, 0, 3, 0);

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(0).trigger('mousedown'); //Insert row above

      expect(afterCreateRowCallback).toHaveBeenCalledWith(1, 1, undefined, undefined, undefined);
      expect(countRows()).toEqual(5);
    });

    it("should insert row above selection (reverse selection)", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      var afterCreateRowCallback = jasmine.createSpy('afterCreateRowCallback');
      hot.addHook('afterCreateRow', afterCreateRowCallback);

      expect(countRows()).toEqual(4);

      selectCell(3, 0, 1, 0);

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(0).trigger('mousedown'); //Insert row above

      expect(afterCreateRowCallback).toHaveBeenCalledWith(1, 1, undefined, undefined, undefined);
      expect(countRows()).toEqual(5);
    });

    it("should insert row below selection", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      var afterCreateRowCallback = jasmine.createSpy('afterCreateRowCallback');
      hot.addHook('afterCreateRow', afterCreateRowCallback);

      expect(countRows()).toEqual(4);

      selectCell(1, 0, 3, 0);

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(1).trigger('mousedown'); //Insert row above

      expect(afterCreateRowCallback).toHaveBeenCalledWith(4, 1, undefined, undefined, undefined);
      expect(countRows()).toEqual(5);
    });

    it("should insert row below selection (reverse selection)", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      var afterCreateRowCallback = jasmine.createSpy('afterCreateRowCallback');
      hot.addHook('afterCreateRow', afterCreateRowCallback);

      expect(countRows()).toEqual(4);

      selectCell(3, 0, 1, 0);

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(1).trigger('mousedown'); //Insert row below

      expect(afterCreateRowCallback).toHaveBeenCalledWith(4, 1, undefined, undefined, undefined);
      expect(countRows()).toEqual(5);
    });

    it("should insert column on the left of selection", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      var afterCreateColCallback = jasmine.createSpy('afterCreateColCallback');
      hot.addHook('afterCreateCol', afterCreateColCallback);

      expect(countCols()).toEqual(4);

      selectCell(0, 1, 0, 3);

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(2).trigger('mousedown'); //Insert col left

      expect(afterCreateColCallback).toHaveBeenCalledWith(1, 1, undefined, undefined, undefined);
      expect(countCols()).toEqual(5);
    });

    it("should insert column on the left of selection (reverse selection)", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      var afterCreateColCallback = jasmine.createSpy('afterCreateColCallback');
      hot.addHook('afterCreateCol', afterCreateColCallback);

      expect(countCols()).toEqual(4);

      selectCell(0, 3, 0, 1);

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(2).trigger('mousedown'); //Insert col left

      expect(afterCreateColCallback).toHaveBeenCalledWith(1, 1, undefined, undefined, undefined);
      expect(countCols()).toEqual(5);
    });

    it("should insert column on the right of selection", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      var afterCreateColCallback = jasmine.createSpy('afterCreateColCallback');
      hot.addHook('afterCreateCol', afterCreateColCallback);

      expect(countCols()).toEqual(4);

      selectCell(0, 1, 0, 3);

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(3).trigger('mousedown'); //Insert col right

      expect(afterCreateColCallback).toHaveBeenCalledWith(4, 1, undefined, undefined, undefined);
      expect(countCols()).toEqual(5);
    });

    it("should insert column on the right of selection (reverse selection)", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      var afterCreateColCallback = jasmine.createSpy('afterCreateColCallback');
      hot.addHook('afterCreateCol', afterCreateColCallback);

      expect(countCols()).toEqual(4);

      selectCell(0, 3, 0, 1);

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(3).trigger('mousedown'); //Insert col right

      expect(afterCreateColCallback).t
    });

    it("should remove selected rows", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      var afterRemoveRowCallback = jasmine.createSpy('afterRemoveRowCallback');
      hot.addHook('afterRemoveRow', afterRemoveRowCallback);

      expect(countRows()).toEqual(4);

      selectCell(1, 0, 3, 0);

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(4).trigger('mousedown'); //Remove row

      expect(afterRemoveRowCallback).toHaveBeenCalledWith(1, 3, undefined, undefined, undefined);
      expect(countRows()).toEqual(1);
    });

    it("should remove selected rows (reverse selection)", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      var afterRemoveRowCallback = jasmine.createSpy('afterRemoveRowCallback');
      hot.addHook('afterRemoveRow', afterRemoveRowCallback);

      expect(countRows()).toEqual(4);

      selectCell(3, 0, 1, 0);

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(4).trigger('mousedown'); //Remove row

      expect(afterRemoveRowCallback).toHaveBeenCalledWith(1, 3, undefined, undefined, undefined);
      expect(countRows()).toEqual(1);
    });

    it("should remove selected columns", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      var afterRemoveColCallback = jasmine.createSpy('afterRemoveColCallback');
      hot.addHook('afterRemoveCol', afterRemoveColCallback);

      expect(countCols()).toEqual(4);

      selectCell(0, 1, 0, 3);

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(5).trigger('mousedown'); //Remove col

      expect(afterRemoveColCallback).toHaveBeenCalledWith(1, 3, undefined, undefined, undefined);
      expect(countCols()).toEqual(1);
    });

    it("should remove selected columns (reverse selection)", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      var afterRemoveColCallback = jasmine.createSpy('afterRemoveColCallback');
      hot.addHook('afterRemoveCol', afterRemoveColCallback);

      expect(countCols()).toEqual(4);

      selectCell(0, 3, 0, 1);

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(5).trigger('mousedown'); //Remove col

      expect(afterRemoveColCallback).toHaveBeenCalledWith(1, 3, undefined, undefined, undefined);
      expect(countCols()).toEqual(1);
    });

    it("should undo changes", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      selectCell(0, 0);

      expect(getDataAtCell(0, 0)).toEqual('A0');

      setDataAtCell(0, 0, 'XX');

      expect(getDataAtCell(0, 0)).toEqual('XX');

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(6).trigger('mousedown'); //Undo

      expect(getDataAtCell(0, 0)).toEqual('A0');
    });

    it("should redo changes", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: true
      });

      selectCell(0, 0);

      expect(getDataAtCell(0, 0)).toEqual('A0');

      setDataAtCell(0, 0, 'XX');

      expect(getDataAtCell(0, 0)).toEqual('XX');

      hot.undo();

      expect(getDataAtCell(0, 0)).toEqual('A0');

      contextMenu();

      $(hot.contextMenu.menu).find('tbody td').not('.htSeparator').eq(7).trigger('mousedown'); //Redo

      expect(getDataAtCell(0, 0)).toEqual('XX');
    });

    it("should display only the specified actions", function () {
      var hot = handsontable({
        data: createSpreadsheetData(4, 4),
        contextMenu: ['remove_row', 'undo']
      });

      contextMenu();

      expect($(hot.contextMenu.menu).find('tbody td').length).toEqual(2);
    });



  });

  describe("disabling actions", function () {

    it("should disable undo and redo action if undoRedo plugin is not enabled ", function () {
      var hot = handsontable({
        contextMenu: true,
        undoRedo: false
      });

      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      expect($menu.find('tbody td:eq(9)').text()).toEqual('Undo');
      expect($menu.find('tbody td:eq(9)').hasClass('htDisabled')).toBe(true);
      expect($menu.find('tbody td:eq(10)').text()).toEqual('Redo');
      expect($menu.find('tbody td:eq(10)').hasClass('htDisabled')).toBe(true);

    });

    it("should disable undo when there is nothing to undo ", function () {
      var hot = handsontable({
        contextMenu: true
      });

      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      expect(hot.undoRedo.isUndoAvailable()).toBe(false);
      expect($menu.find('tbody td:eq(9)').text()).toEqual('Undo');
      expect($menu.find('tbody td:eq(9)').hasClass('htDisabled')).toBe(true);

      closeContextMenu();

      setDataAtCell(0, 0, 'foo');

      contextMenu();

      expect(hot.undoRedo.isUndoAvailable()).toBe(true);
      expect($menu.find('tbody td:eq(9)').hasClass('htDisabled')).toBe(false);

    });

    it("should disable redo when there is nothing to redo ", function () {
      var hot = handsontable({
        contextMenu: true
      });

      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      expect(hot.undoRedo.isRedoAvailable()).toBe(false);
      expect($menu.find('tbody td:eq(10)').text()).toEqual('Redo');
      expect($menu.find('tbody td:eq(10)').hasClass('htDisabled')).toBe(true);

      closeContextMenu();

      setDataAtCell(0, 0, 'foo');
      hot.undo();

      contextMenu();

      expect(hot.undoRedo.isRedoAvailable()).toBe(true);
      expect($menu.find('tbody td:eq(10)').hasClass('htDisabled')).toBe(false);

    });

    it('should disable Insert row in context menu when maxRows is reached', function () {
      var hot = handsontable({
        contextMenu: true,
        maxRows: 6
      });

      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      expect($menu.find('tbody td:eq(0)').text()).toEqual('Insert row above');
      expect($menu.find('tbody td:eq(0)').hasClass('htDisabled')).toBe(false);
      expect($menu.find('tbody td:eq(1)').text()).toEqual('Insert row below');
      expect($menu.find('tbody td:eq(1)').hasClass('htDisabled')).toBe(false);

      closeContextMenu();

      alter('insert_row');

      contextMenu();

      expect($menu.find('tbody td:eq(0)').hasClass('htDisabled')).toBe(true);
      expect($menu.find('tbody td:eq(1)').hasClass('htDisabled')).toBe(true);

    });

    it('should disable Insert col in context menu when maxCols is reached', function () {
      var hot = handsontable({
        contextMenu: true,
        maxCols: 6
      });

      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      expect($menu.find('tbody td:eq(3)').text()).toEqual('Insert column on the left');
      expect($menu.find('tbody td:eq(3)').hasClass('htDisabled')).toBe(false);
      expect($menu.find('tbody td:eq(4)').text()).toEqual('Insert column on the right');
      expect($menu.find('tbody td:eq(4)').hasClass('htDisabled')).toBe(false);

      closeContextMenu();

      alter('insert_col');

      contextMenu();

      expect($menu.find('tbody td:eq(3)').hasClass('htDisabled')).toBe(true);
      expect($menu.find('tbody td:eq(4)').hasClass('htDisabled')).toBe(true);

    });
  });

  describe("custom options", function () {
    it("should have custom items list", function () {

      var callback1 = jasmine.createSpy('callback1');
      var callback2 = jasmine.createSpy('callback2');

      var hot = handsontable({
        contextMenu: {
          items: {
            cust1: {
              name: 'CustomItem1',
              callback: callback1
            },
            cust2: {
              name: 'CustomItem2',
              callback: callback2
            }
          }
        }
      });

      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      expect($menu.find('tbody td').length).toEqual(2);
      expect($menu.find('tbody td').text()).toEqual(['CustomItem1', 'CustomItem2'].join(''));

      $menu.find('tbody td:eq(0)').trigger('mousedown');

      expect(callback1.calls.length).toEqual(1);
      expect(callback2.calls.length).toEqual(0);

      contextMenu();
      $menu.find('tbody td:eq(1)').trigger('mousedown');

      expect(callback1.calls.length).toEqual(1);
      expect(callback2.calls.length).toEqual(1);

    });

    it("should enable to define item options globally", function () {

      var callback = jasmine.createSpy('callback');

      var hot = handsontable({
        contextMenu: {
          callback: callback,
          items: {
            cust1: {
              name: 'CustomItem1'
            },
            cust2: {
              name: 'CustomItem2'
            }
          }
        }
      });

      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      $menu.find('tbody td:eq(0)').trigger('mousedown');

      expect(callback.calls.length).toEqual(1);

      contextMenu();
      $menu.find('tbody td:eq(1)').trigger('mousedown');

      expect(callback.calls.length).toEqual(2);

    });

    it("should override default items options", function () {
      var callback = jasmine.createSpy('callback');

      var hot = handsontable({
        contextMenu: {
          items: {
            'remove_row': {
              callback: callback
            },
            'remove_col': {
              name: 'Delete column'
            }
          }
        }
      });

      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      expect($menu.find('tbody td').length).toEqual(2);
      expect($menu.find('tbody td').text()).toEqual(['Remove row', 'Delete column'].join(''));

      $menu.find('tbody td:eq(0)').trigger('mousedown');

      expect(callback.calls.length).toEqual(1);

      expect(countCols()).toEqual(5);

      contextMenu();
      $menu.find('tbody td:eq(1)').trigger('mousedown');

      expect(countCols()).toEqual(4);

    });

    it("should fire item callback after item has been clicked", function () {

      var customItem = {
        name: 'Custom item',
        callback: function(){}
      };

      spyOn(customItem, 'callback');

      var hot = handsontable({
        contextMenu: {
          items: {
            'customItemKey' : customItem
          }
        }
      });

      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      $menu.find('tbody td:eq(0)').trigger('mousedown');

      expect(customItem.callback.calls.length).toEqual(1);
      expect(customItem.callback.calls[0].args[0]).toEqual('customItemKey');

    });

  });

  describe("keyboard navigation", function () {

    describe("no item selected", function () {

      it("should select the first item in menu, when user hits ARROW_DOWN", function () {

        var hot = handsontable({
          contextMenu: true
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        expect(menuHot.getSelected()).toBeUndefined();

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);

      });

      it("should select the first NOT DISABLED item in menu, when user hits ARROW_DOWN", function () {

        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1',
                disabled: true
              },
              item2: {
                name: 'Item2',
                disabled: true
              },
              item3: {
                name: 'Item3'
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        expect(menuHot.getSelected()).toBeUndefined();

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([2, 0, 2, 0]);

      });

      it("should NOT select any items in menu, when user hits ARROW_DOWN and there is no items enabled", function () {

        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1',
                disabled: true
              },
              item2: {
                name: 'Item2',
                disabled: true
              },
              item3: {
                name: 'Item3',
                disabled: true
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        expect(menuHot.getSelected()).toBeUndefined();

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toBeUndefined();

      });

      it("should select the last item in menu, when user hits ARROW_UP", function () {

        var hot = handsontable({
          contextMenu: {
            items: {
              item1: 'Item1',
              item2: 'Item2',
              item3: 'Item3'
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        expect(menuHot.getSelected()).toBeUndefined();

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([2, 0, 2, 0]);

      });

      it("should select the last NOT DISABLED item in menu, when user hits ARROW_UP", function () {

        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1'
              },
              item2: {
                name: 'Item2',
                disabled: true
              },
              item3: {
                name: 'Item3',
                disabled: true
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        expect(menuHot.getSelected()).toBeUndefined();

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);

      });

      it("should NOT select any items in menu, when user hits ARROW_UP and there is no items enabled", function () {

        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1',
                disabled: true
              },
              item2: {
                name: 'Item2',
                disabled: true
              },
              item3: {
                name: 'Item3',
                disabled: true
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        expect(menuHot.getSelected()).toBeUndefined();

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toBeUndefined();

      });

    });

    describe("item selected", function () {

      it("should select next item when user hits ARROW_DOWN", function () {
        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1'
              },
              item2: {
                name: 'Item2'
              },
              item3: {
                name: 'Item3'
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([1, 0, 1, 0]);

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([2, 0, 2, 0]);
      });

      it("should select next item (skipping disabled items) when user hits ARROW_DOWN", function () {
        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1'
              },
              item2: {
                name: 'Item2',
                disabled: true
              },
              item3: {
                name: 'Item3'
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([2, 0, 2, 0]);
      });

      it("should select next item (skipping separators) when user hits ARROW_DOWN", function () {
        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1'
              },
              sep1: Handsontable.ContextMenu.SEPARATOR,
              item2: {
                name: 'Item2'
              },
              item3: {
                name: 'Item3'
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([2, 0, 2, 0]);

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([3, 0, 3, 0]);
      });

      it("should not change selection when last item is selected and user hits ARROW_DOWN", function () {
        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1'
              },
              item2: {
                name: 'Item2'
              },
              item3: {
                name: 'Item3'
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([1, 0, 1, 0]);

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([2, 0, 2, 0]);

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([2, 0, 2, 0]);
      });

      it("should not change selection when last enabled item is selected and user hits ARROW_DOWN", function () {
        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1'
              },
              item2: {
                name: 'Item2'
              },
              item3: {
                name: 'Item3',
                disabled: true
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([1, 0, 1, 0]);

        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([1, 0, 1, 0]);
      });

      it("should select next item when user hits ARROW_UP", function () {
        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1'
              },
              item2: {
                name: 'Item2'
              },
              item3: {
                name: 'Item3'
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([2, 0, 2, 0]);

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([1, 0, 1, 0]);

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);
      });

      it("should select next item (skipping disabled items) when user hits ARROW_UP", function () {
        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1'
              },
              item2: {
                name: 'Item2',
                disabled: true
              },
              item3: {
                name: 'Item3'
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([2, 0, 2, 0]);

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);
      });

      it("should select next item (skipping separators) when user hits ARROW_UP", function () {
        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1'
              },
              sep1: Handsontable.ContextMenu.SEPARATOR,
              item2: {
                name: 'Item2'
              },
              item3: {
                name: 'Item3'
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([3, 0, 3, 0]);

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([2, 0, 2, 0]);

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);
      });

      it("should not change selection when first item is selected and user hits ARROW_UP", function () {
        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1'
              },
              item2: {
                name: 'Item2'
              },
              item3: {
                name: 'Item3'
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([2, 0, 2, 0]);

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([1, 0, 1, 0]);

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);
      });

      it("should not change selection when first enabled item is selected and user hits ARROW_UP", function () {
        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1',
                disabled: true
              },
              item2: {
                name: 'Item2'
              },
              item3: {
                name: 'Item3'
              }
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([2, 0, 2, 0]);

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([1, 0, 1, 0]);

        keyDownUp('arrow_up');

        expect(menuHot.getSelected()).toEqual([1, 0, 1, 0]);
      });

      it("should perform a selected item action, when user hits ENTER", function () {

        var itemAction = jasmine.createSpy('itemAction');

        var hot = handsontable({
          contextMenu: {
            items: {
              item1: {
                name: 'Item1',
                callback: itemAction
              },
              item2: 'Item2'
            }
          }
        });

        contextMenu();

        var menuHot = $(hot.contextMenu.menu).handsontable('getInstance');


        keyDownUp('arrow_down');

        expect(menuHot.getSelected()).toEqual([0, 0, 0, 0]);

        expect(itemAction).not.toHaveBeenCalled();

        keyDownUp('enter');

        expect(itemAction).toHaveBeenCalled();
        expect($(hot.contextMenu.menu).is(':visible')).toBe(false);

      });

    });

    it("should close menu when user hits ESC", function () {

      var hot = handsontable({
        contextMenu: true
      });

      contextMenu();

      expect($(hot.contextMenu.menu).is(':visible')).toBe(true);

      keyDownUp('esc');

      expect($(hot.contextMenu.menu).is(':visible')).toBe(false);

    });

  });

  describe("working with multiple tables", function () {

    beforeEach(function () {
      this.$container2 = $('<div id="' + id + '-2"></div>').appendTo('body');
    });

    afterEach(function () {
      if(this.$container2){
        this.$container2.handsontable('destroy');
        this.$container2.remove();
      }
    });

    it("should apply enabling/disabling contextMenu using updateSetting only to particular instance of HOT ", function () {
      var hot1 = handsontable({
        contextMenu: false
      });

      this.$container2.handsontable({
        contextMenu: true
      });

      var hot2 = this.$container2.handsontable('getInstance');
      var contextMenuContainer = $('.htContextMenu');

      expect(contextMenuContainer.length).toEqual(1);

      contextMenu();
      expect(hot1.contextMenu).toBeUndefined();
      expect(contextMenuContainer.is(':visible')).toBe(false);

      contextMenu2();
      expect(hot2.contextMenu).toBeDefined();
      expect($(hot2.contextMenu.menu).is(':visible')).toBe(true);

      mouseDown(hot2.rootElement); //close menu


      hot1.updateSettings({
        contextMenu: true
      });

      hot2.updateSettings({
        contextMenu: false
      });

      contextMenuContainer = $('.htContextMenu');

      expect(contextMenuContainer.length).toEqual(1);

      contextMenu2();
      expect(hot2.contextMenu).toBeUndefined();

      contextMenu();
      expect($(hot1.contextMenu.menu).is(':visible')).toBe(true);

      function contextMenu2() {
        var hot = spec().$container2.data('handsontable');
        var selected = hot.getSelected();

        if(!selected){
          hot.selectCell(0, 0);
          selected = hot.getSelected();
        }

        var cell = hot.getCell(selected[0], selected[1]);
        var cellOffset = $(cell).offset();

        var ev = $.Event('contextmenu', {
          pageX: cellOffset.left,
          pageY: cellOffset.top
        });

        $(cell).trigger(ev);
      }

    });

    it("should create only one DOM node for contextMenu per page ", function () {


      var hot1 = handsontable({
        contextMenu: false
      });

      this.$container2.handsontable({
        contextMenu: false
      });

      var hot2 = this.$container2.handsontable('getInstance');
      var contextMenuContainer = $('.htContextMenu');

      expect(contextMenuContainer.length).toEqual(0);

      hot1.updateSettings({
        contextMenu: true
      });

      contextMenuContainer = $('.htContextMenu');

      expect(contextMenuContainer.length).toEqual(1);

      hot2.updateSettings({
        contextMenu: true
      });

      contextMenuContainer = $('.htContextMenu');

      expect(contextMenuContainer.length).toEqual(1);




    });

    it("should remove contextMenu DOM nodes when there is no HOT instance on the page, which has contextMenu enabled ", function () {
      var hot1 = handsontable({
        contextMenu: true
      });

      this.$container2.handsontable({
        contextMenu: true
      });

      var hot2 = this.$container2.handsontable('getInstance');
      var contextMenuContainer = $('.htContextMenu');

      expect(contextMenuContainer.length).toEqual(1);

      hot1.updateSettings({
        contextMenu: true
      });

      hot2.updateSettings({
        contextMenu: false
      });

      contextMenuContainer = $('.htContextMenu');

      expect(contextMenuContainer.length).toEqual(1);

      hot1.updateSettings({
        contextMenu: false
      });

      hot2.updateSettings({
        contextMenu: false
      });

      contextMenuContainer = $('.htContextMenu');

      expect(contextMenuContainer.length).toEqual(0);


    });

    it("should perform a contextMenu action only for particular instance of HOT ", function () {
      var hot1 = handsontable({
        contextMenu: true
      });

      this.$container2.handsontable({
        contextMenu: true
      });

      var hot2 = this.$container2.handsontable('getInstance');
      var contextMenuContainer = $('.htContextMenu');

      hot1.selectCell(0, 0);
      contextMenu();

      expect(hot1.countRows()).toEqual(5);
      expect(hot2.countRows()).toEqual(5);

      $(hot1.contextMenu.menu).find('tr td:eq("0")').mousedown(); //insert row above

      expect(hot1.countRows()).toEqual(6);
      expect(hot2.countRows()).toEqual(5);

      hot2.selectCell(0, 0);
      contextMenu2();

      expect(hot1.countRows()).toEqual(6);
      expect(hot2.countRows()).toEqual(5);

      $(hot2.contextMenu.menu).find('tr td:eq("0")').mousedown(); //insert row above

      expect(hot1.countRows()).toEqual(6);
      expect(hot2.countRows()).toEqual(6);

      function contextMenu2() {
        var hot = spec().$container2.data('handsontable');
        var selected = hot.getSelected();

        if(!selected){
          hot.selectCell(0, 0);
          selected = hot.getSelected();
        }

        var cell = hot.getCell(selected[0], selected[1]);
        var cellOffset = $(cell).offset();

        var ev = $.Event('contextmenu', {
          pageX: cellOffset.left,
          pageY: cellOffset.top
        });

        $(cell).trigger(ev);
      }

    });

  });

  describe("context menu with native scroll", function () {

    beforeEach(function () {
      var wrapper = $('<div></div>').css({
        width: 400,
        height: 200,
        overflow: 'scroll'
      });

      this.$wrapper = this.$container.wrap(wrapper).parent();
    });

    afterEach(function () {
      if (this.$container) {
        destroy();
        this.$container.remove();
      }
      this.$wrapper.remove();
    });

    it("should display menu table is not scrolled", function () {


      var hot = handsontable({
        data: createSpreadsheetData(40, 30),
        colWidths: 50, //can also be a number or a function
        rowHeaders: true,
        colHeaders: true,
        contextMenu: true,
        nativeScrollbars: true
      });

      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      expect($menu.is(':visible')).toBe(true);

    });

    it("should display menu table is scrolled", function () {


      var hot = handsontable({
        data: createSpreadsheetData(40, 30),
        colWidths: 50, //can also be a number or a function
        rowHeaders: true,
        colHeaders: true,
        contextMenu: true,
        nativeScrollbars: true
      });

      this.$wrapper.scrollTop(300);
      this.$wrapper.scroll();

      selectCell(15, 3);
      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      expect($menu.is(':visible')).toBe(true);

    });

    it("should close menu, when table is scrolled", function () {


      var hot = handsontable({
        data: createSpreadsheetData(40, 30),
        colWidths: 50, //can also be a number or a function
        rowHeaders: true,
        colHeaders: true,
        contextMenu: true,
        nativeScrollbars: true
      });

      selectCell(15, 3);
      var scrollTop = this.$wrapper.scrollTop();
      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      expect($menu.is(':visible')).toBe(true);

      this.$wrapper.scrollTop(scrollTop + 60).scroll();

      expect($menu.is(':visible')).toBe(false);

      contextMenu();

      expect($menu.is(':visible')).toBe(true);

      this.$wrapper.scrollTop(scrollTop + 100).scroll();

      expect($menu.is(':visible')).toBe(false)

    });

    it("should not attempt to close menu, when table is scrolled and the menu is already closed", function () {


      var hot = handsontable({
        data: createSpreadsheetData(40, 30),
        colWidths: 50, //can also be a number or a function
        rowHeaders: true,
        colHeaders: true,
        contextMenu: true,
        nativeScrollbars: true
      });

      selectCell(15, 3);
      var scrollTop = this.$wrapper.scrollTop();
      contextMenu();
      var $menu = $(hot.contextMenu.menu);

      expect($menu.is(':visible')).toBe(true);

      this.$wrapper.scrollTop(scrollTop + 60).scroll();

      expect($menu.is(':visible')).toBe(false);

      spyOn(hot.contextMenu, 'close');

      this.$wrapper.scrollTop(scrollTop + 100).scroll();

      expect(hot.contextMenu.close).not.toHaveBeenCalled();

    });

  });


});