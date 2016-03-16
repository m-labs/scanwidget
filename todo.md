## To Fix (Bugs)

## To Modify (Not technically broken, but needs to be changed on request)

## To Implement

## Improvements
* Add keyboard shortcuts for "Snap Range" (ctrl-p) and "View Range" (ctrl-i).
  Needs focus.
* When dragging a slider, it should snap (-> spinboxes) to "nice" values.
  Something like rounding to Ticker(n=handlePositions).step(a,b) should be good.
* Spinbox buttons should increment/decrement by Ticker(n=handlePositions).step(a,b)
  as well
* Move Reset (a.k.a recalculate arguments) into context menu to save
  space/declutter.
