## To Fix (Bugs)
* Check that recalculating the zoom transform in fact has a relative error of 10^-15, not absolute error. If latter, rethink transform.
* Remove asserts

## To Modify (Not technically broken, but needs to be changed on request)

## To Implement
* Drag modes:
    * drag axis, groove: move axis origin
    * drag a handle: move the handle (done)
    * shift-drag axis, groove: move both sliders (and thus all scanned points, but not the axis, analogous to shift-wheel vs wheel)
    * shift-drag handle: nothing (done)
    * shift-wheel on handles, groove, axis: change npoints (done)
    * wheel and ctrl-wheel on groove, axis, handles: zoom (done)
        * Rationale: the behavior that could be expected from a single handle, where wheel moves "the" handle does not work here.
          Keep ctrl-wheel for this as it matches other apps' behaviors and bare wheel is usually diverted to scrolling a higher encapsulating widget.

## Improvements
* Add keyboard shortcuts for "Snap Range" (ctrl-p) and "View Range" (ctrl-i).
  Needs focus.
* When dragging a slider, it should snap (-> spinboxes) to "nice" values.
  Something like rounding to Ticker(n=handlePositions).step(a,b) should be good.
* Spinbox buttons should increment/decrement by Ticker(n=handlePositions).step(a,b)
  as well
* Move Reset (a.k.a recalculate arguments) into context menu to save
  space/declutter.
