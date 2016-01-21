describe('WalkontableRowStrategy', function () {
  var source;
  var fakeWalkontableInstance = {
    getSetting : function(){}
  };

  function allCells25(i) {
    if (source[i] !== void 0) {
      return 25;
    }
  }

  function allCellsPlus100(i) {
    if (source[i] !== void 0) {
      return i + 100;
    }
  }

  it("cell strategy should add only as many rows as it fits in the viewport", function () {
    source = [0, 1, 2, 5, 6, 7, 8, 9, 10];
    var viewportSize = 100;
    var strategy = new WalkontableRowStrategy(fakeWalkontableInstance, viewportSize, allCells25);
    for (var i = 0; i < source.length; i++) {
      strategy.add(i);
    }
    expect(strategy.cellSizes).toEqual([25, 25, 25, 25]);
  });

  it("should show all cells if containerSize is Infinity", function () {
    source = [0, 1, 2, 5, 6, 7, 8, 9, 10];
    var strategy = new WalkontableRowStrategy(fakeWalkontableInstance, Infinity, allCells25);
    for (var i = 0; i < source.length; i++) {
      strategy.add(i);
    }
    expect(strategy.cellCount).toEqual(source.length);
  });

//getSize

  it("getSize should return cell size at given index", function () {
    source = [0, 1, 2, 3, 4];
    var strategy = new WalkontableRowStrategy(fakeWalkontableInstance, Infinity, allCellsPlus100);
    for (var i = 0; i < source.length; i++) {
      strategy.add(i);
    }
    expect(strategy.cellSizes).toEqual([100, 101, 102, 103, 104]);
    expect(strategy.getSize(0)).toEqual(100);
    expect(strategy.getSize(4)).toEqual(104);
  });
})
;
