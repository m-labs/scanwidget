## To Fix (Bugs)
* At large zooms, the sliders start taking the wrong positions due to floating point errors?
* Check that recalculating the zoom transform in fact has a relative error of 10^-15, not absolute error. If latter, rethink transform.
* Remove asserts (or catch AssertionFailure) and just refuse to honor zooms at some point.

## To Modify (Not technically broken, but needs to be changed on request)
* Change slider behavior so that sliders can cross/overlap.
    * Rename Min/Max (and Lower/Upper?) terminology to Start/Stop

## To Implement
* Implement slider hiding when zoom causes sliders to disappear.
* Add number of points functionality
    * change on shift-wheelEvent
* Drag modes:
    * drag axis: move axis origin
    * drag groove: move axis origin
    * drag handle: move handle (as it is now)
    * shift-drag axis: move both sliders (and thus all scanned points, analogous to shift-wheelEvent)
    * shift-drag groove: move both sliders (and thus all points)
    * shift-drag handle: nothing
    * wheel on groove: zoom axis:
        * sidenote: the behavior that could be expected from a single handle, where wheel moves "the" handle does not work here. it might be better to do nothing than something that is unexpected
    * wheel on handle: nothing (as above)
* Convert FitToView and ZoomToFit to context menu, add Reset.
* Axis widget should capture scroll events from sliders.
* To be discussed: drag and shift-drag on the groove

## Improvements
* When dragging a slider, it should snap (-> spinboxes) to "nice" values.
  Something like rounding to Ticker(n=handlePositions).step(a,b) should be good.
* Spinbox buttons should increment/decrement by Ticker(n=handlePositions).step(a,b)
  as well
