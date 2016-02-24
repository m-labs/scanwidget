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
    * visualize on axis
    * change on shift-wheelEvent
* Drag modes:
    * drag axis: move axis origin
    * shift-drag axis: move both sliders (and thus all scanned points, analogous to shift-wheelEvent)
* Convert FitToView and ZoomToFit to context menu, add Reset.
* Add tick mark visualization for number of points.
* Axis widget should capture scroll events from slider.

## Improvements
* When dragging a slider, it should snap (-> spinboxes) to "nice" values. The
  Something like rounding to Ticker().step() should be sufficient.
