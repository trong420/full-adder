# Example extraction deck

# Initialise boolean package. 
ui = cvar.uiptr
cv = ui.getEditCellView()
geomBegin(cv)
lib = cv.lib()

print("\n# Loading pcells")
#ui.loadPCell(lib.libName(), "nch_ex")
#ui.loadPCell(lib.libName(), "pch_ex")
#ui.loadPCell(lib.libName(), "rppoly_ex")
#ui.loadPCell(lib.libName(), "nmoscap_ex")

print("# Get raw layers")
nwell     = geomGetShapes("nwell", "drawing")
active    = geomGetShapes("od", "drawing")
poly      = geomGetShapes("polyg", "drawing")
nimp      = geomGetShapes("nimp", "drawing")
pimp      = geomGetShapes("pimp", "drawing")
cont      = geomGetShapes("cont", "drawing")
metal1    = geomGetShapes("metal1", "drawing")
via12     = geomGetShapes("via12", "drawing")
metal2    = geomGetShapes("metal2", "drawing")
via23     = geomGetShapes("via23", "drawing")
metal3    = geomGetShapes("metal3", "drawing")
rpo       = geomGetShapes("rpo", "drawing")
cap       = geomGetShapes("cap", "drawing")

print("# Form derived layers")
bkgnd     = geomBkgnd()
psub      = geomAndNot(bkgnd, nwell)
# If there are no poly resistors, don't bother to process them.
if geomNumShapes(rpo) > 0 :
	pres      = geomAnd(poly, rpo)
	polyg     = geomAndNot(poly, rpo)
else :
	polyg = poly
gate      = geomAnd(polyg, active)
diff      = geomAndNot(active, gate)
ndiff     = geomAnd(diff, nimp)
pdiff     = geomAnd(diff, pimp)
ntap      = geomAnd(ndiff, nwell)
ptap      = geomAndNot(pdiff, nwell)
# If there are no mos capacitors, don't bother to process them.
if geomNumShapes(cap) > 0 :
	mosgate   = geomAndNot(gate, cap)
	ngate     = geomAnd(mosgate, nimp)
	pgate     = geomAnd(mosgate, pimp)
	mcap      = geomAnd(gate, cap)
else :
	ngate     = geomAnd(gate, nimp)
	pgate     = geomAnd(gate, pimp)

print("# Label nodes")
# This must be done BEFORE geomConnect.
geomLabel(polyg, "potxt", "drawing")
geomLabel(metal1, "m1txt", "drawing")
geomLabel(metal2, "m2txt", "drawing")

print("# Form connectivity")
geomConnect( [
              [ptap, pdiff, psub],
              [ntap, ndiff, nwell],
              [cont, ndiff, pdiff, polyg, metal1],
              [via12, metal1, metal2],
              [via23, metal2, metal3],
	     ] )

# Save connectivity to extracted view. Saved layers must be
# ones previously connected by geomConnect. Any derived
# layers must be saved to a named layer (e.g. psub below)
print("# Save interconnect")
saveInterconnect([
                [psub, "psub"],
		nwell,
		[ntap, "od"],
		[ptap, "od"],
		[ndiff, "od"],
		[pdiff, "od"],
		[polyg, "polyg"],
		cont,
		metal1,
		via12,
		metal2,
		via23,
		metal3])

# Extract MOS devices. Device terminal layers *must* exist in
# the extracted view as a result of saveInterconnect.
# In this case we are using pcell devices which will be
# created according to the recognition region polygon.
print("# Extract MOS devices")
extractMOS("nch_ex", ngate, polyg, active, psub)
extractMOS("pch_ex", pgate, polyg, active, nwell)

# Extract resistors. Device terminal layers must exist in
# extracted view as a result of saveInterconnect.
if geomNumShapes(rpo) > 0 :
	print("# Extract poly resistors")
	extractRes("rppoly_ex", pres, polyg)

# Extract MOS capacitors. Device terminal layers must exist in
# extracted view as a result of saveInterconnect.
if geomNumShapes(cap) > 0 :
	print("# Extract MOS capacitors")
	extractMosCap("nmoscap_ex", mcap, polyg, active)

# Extract parasitics. 
#extractParasitic(metal1, 1.15e-14, 1.50e-14, "VSS")
#extractParasitic2(metal1, metal2, 2.0e-14, 2.0e-14)
#extractParasitic3D("vss", "vss")

# Exit boolean package, freeing memory
print("# Extraction completed.")
geomEnd()

# Open the extracted view
ui.openCellView(lib.libName(), cv.cellName(), "extracted")
