## To Fix (Bugs)
* At large zooms, the sliders start taking the wrong positions due to floating point errors?
* Check that recalculating the zoom transform in fact has a relative error of 10^-15, not absolute error. If latter, rethink transform.
* Remove asserts (or catch AssertionFailure) and just refuse to honor zooms at some point.
* Many more slider positions than 100

## To Modify (Not technically broken, but needs to be changed on request)
* Change slider behavior so that sliders can cross/overlap.
    * Rename Min/Max (and Lower/Upper?) terminology to Start/Stop
* When widget is large vertically, the prefix (offset and magnitude) are
  painted far away from the axis

## To Implement
* Implement slider hiding when zoom causes sliders to disappear.
* Add number of points functionality
    * Add tick mark visualization on axis for number of points.
    * change on shift-wheelEvent
* Drag modes:
    * drag axis: move axis origin
    * shift-drag axis: move both sliders (and thus all scanned points, analogous to shift-wheelEvent)
* Convert FitToView and ZoomToFit to context menu, add Reset.
* Axis widget should capture scroll events from sliders.
* To be discussed: drag and shift-drag on the groove

## Improvements
* When dragging a slider, it should snap (-> spinboxes) to "nice" values.
  Something like rounding to Ticker(n=handlePositions).step(a,b) should be good.
* Spinbox buttons should increment/decrement by Ticker(n=handlePositions).step(a,b)
  as well
