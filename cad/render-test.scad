// =============================================================================
// render-test.scad — does frame.scad's geometry actually reach a caller?
// =============================================================================
// Put this file in the SAME FOLDER as frame.scad and frame_params.scad, open it
// in OpenSCAD and press F5 (preview, not F6).
//
// You should see six parts in a row. Report back:
//   1. WHICH of the six appear, left to right, and which are missing.
//   2. Everything in the console window at the bottom — especially any line
//      starting WARNING or ERROR. A line like
//        WARNING: Ignoring unknown variable 'foo'
//      names the failure exactly.
//   3. The version line the echo prints.
//
// If the console pane is hidden: View menu -> Console (or Window -> Console,
// depending on version). Select all in it and copy.
// =============================================================================

include <frame_params.scad>
use <frame.scad>

echo(str(">>> cad_version reported as: ", cad_version));
echo(str(">>> if the line above says 'undef', frame_params.scad is stale"));

translate([   0, 0, 0]) yoke();             // 1
translate([ 130, 0, 0]) base_plate();       // 2
translate([ 230, 0, 0]) cradle();           // 3
translate([ 300, 0, 0]) cradle_cap();       // 4
translate([ 365, 0, 0]) trunnion();         // 5
translate([ 425, 0, 0]) bearing_carrier();  // 6
