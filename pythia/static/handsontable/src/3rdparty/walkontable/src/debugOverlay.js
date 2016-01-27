/**
 * A overlay that renders ALL available rows & columns positioned on top of the original Walkontable instance and all other overlays.
 * Used for debugging purposes to see if the other overlays (that render only part of the rows & columns) are positioned correctly
 * @param instance
 * @constructor
 */
function WalkontableDebugOverlay(instance) {
  this.instance = instance;
  this.init();
  this.clone = this.makeClone('debug');
  this.clone.wtTable.holder.style.opacity = 0.4;
  this.clone.wtTable.holder.style.textShadow = '0 0 2px #ff0000';

  var that = this;
  var lastTimeout;
  var lastX = 0;
  var lastY = 0;
  var overlayContainer = that.clone.wtTable.holder.parentNode;

  $(document.body).on('mousemove.' + this.instance.guid, function (event) {
    if (!that.instance.wtTable.holder.parentNode) {
      return; //removed from DOM
    }
    if ((event.clientX - lastX > -5 && event.clientX - lastX < 5) && (event.clientY - lastY > -5 && event.clientY - lastY < 5)) {
      return; //ignore minor mouse movement
    }
    lastX = event.clientX;
    lastY = event.clientY;
    WalkontableDom.prototype.addClass(overlayContainer, 'wtDebugHidden');
    WalkontableDom.prototype.removeClass(overlayContainer, 'wtDebugVisible');
    clearTimeout(lastTimeout);
    lastTimeout = setTimeout(function () {
      WalkontableDom.prototype.removeClass(overlayContainer, 'wtDebugHidden');
      WalkontableDom.prototype.addClass(overlayContainer, 'wtDebugVisible');
    }, 1000);
  });
}

WalkontableDebugOverlay.prototype = new WalkontableOverlay();

WalkontableDebugOverlay.prototype.resetFixedPosition = function () {
  if (!this.instance.wtTable.holder.parentNode) {
    return; //removed from DOM
  }
  var elem = this.clone.wtTable.holder.parentNode;
  var box = this.instance.wtTable.holder.getBoundingClientRect();
  elem.style.top = Math.ceil(box.top, 10) + 'px';
  elem.style.left = Math.ceil(box.left, 10) + 'px';
};

WalkontableDebugOverlay.prototype.prepare = function () {
};

WalkontableDebugOverlay.prototype.refresh = function (selectionsOnly) {
  this.clone && this.clone.draw(selectionsOnly);
};

WalkontableDebugOverlay.prototype.getScrollPosition = function () {
};

WalkontableDebugOverlay.prototype.getLastCell = function () {
};

WalkontableDebugOverlay.prototype.applyToDOM = function () {
};

WalkontableDebugOverlay.prototype.scrollTo = function () {
};

WalkontableDebugOverlay.prototype.readWindowSize = function () {
};

WalkontableDebugOverlay.prototype.readSettings = function () {
};