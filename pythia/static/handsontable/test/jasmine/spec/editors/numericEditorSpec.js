describe('NumericEditor', function () {
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

  var arrayOfObjects = function () {
    return [
      {id: 1, name: "Ted", lastName: "Right"},
      {id: 2, name: "Frank", lastName: "Honest"},
      {id: 3, name: "Joan", lastName: "Well"},
      {id: 4, name: "Sid", lastName: "Strong"},
      {id: 5, name: "Jane", lastName: "Neat"},
      {id: 6, name: "Chuck", lastName: "Jackson"},
      {id: 7, name: "Meg", lastName: "Jansen"},
      {id: 8, name: "Rob", lastName: "Norris"},
      {id: 9, name: "Sean", lastName: "O'Hara"},
      {id: 10, name: "Eve", lastName: "Branson"}
    ];
  };

  it('should convert numeric value to number (object data source)', function () {

    var onAfterValidate = jasmine.createSpy('onAfterValidate');

    handsontable({
      data: arrayOfObjects(),
      columns: [
        {data: 'id', type: 'numeric'},
        {data: 'name'},
        {data: 'lastName'}
      ],
      afterValidate: onAfterValidate
    });
    selectCell(2, 0);

    keyDown('enter');
    document.activeElement.value = '999';

    destroyEditor();

    waitsFor(function () {
      return onAfterValidate.calls.length > 0;
    }, 'Cell validation', 1000);

    runs(function () {
      expect(typeof getDataAtCell(2, 0)).toEqual('number');
      expect(getDataAtCell(2, 0)).toEqual(999);
    });

  });

  it('should allow custom validator', function () {

    var onAfterValidate = jasmine.createSpy('onAfterValidate');

    handsontable({
      data: arrayOfObjects(),
      allowInvalid: false,
      columns: [
        {data: 'id', type: 'numeric', validator: function(val, cb) {
          cb(parseInt(val, 10) > 100);
        }},
        {data: 'name'},
        {data: 'lastName'}
      ],
      afterValidate: onAfterValidate
    });
    selectCell(2, 0);

    keyDown('enter');
    document.activeElement.value = '99';

    destroyEditor();

    waitsFor(function () {
      return onAfterValidate.calls.length > 0;
    }, 'Cell validation', 1000);

    runs(function () {
      expect(getDataAtCell(2, 0)).not.toEqual(99); //should be ignored
    });

    runs(function () {
      document.activeElement.value = '999';

      onAfterValidate.reset();
      destroyEditor();
    });

    waitsFor(function () {
      return onAfterValidate.calls.length > 0;
    }, 'Cell validation', 1000);

    runs(function () {
      expect(getDataAtCell(2, 0)).toEqual(999);
    });

  });
});