import rpg.editor.core.*
import rpg.editor.model.*
import org.eclipse.swt.*
import org.eclipse.swt.custom.*
import org.eclipse.swt.events.*
import org.eclipse.swt.graphics.*
import org.eclipse.swt.layout.*
import org.eclipse.swt.widgets.*

try {

final def TAB_COLOUR = new RGB(142, 175, 230);

def display = DisplayHelper.getDisplay();
def shell = DisplayHelper.getShell();

def mapEditor = null
def recentTiles = null
def folder = null

shell.layout = new GridLayout()
shell.text = 'RPG Editor'

def menuBar = new Menu(shell, SWT.BAR)
def menuItem = new MenuItem(menuBar, SWT.CASCADE)
menuItem.text = 'File'
def fileMenu = new Menu(shell, SWT.DROP_DOWN);
menuItem.menu = fileMenu;

// == MENU ITEMS ==

def openTileset = new MenuItem(fileMenu, SWT.PUSH)
openTileset.text = 'Open Tileset'
openTileset.addListener(SWT.Selection, {
	// create new TilePicker
	def tileSet = TileSet.loadTileSet()
	if (tileSet) {
		def tilePicker = new GTilePicker(folder, tileSet);
		tilePicker.tileSelection = recentTiles;
		def item = new CTabItem(folder, SWT.CLOSE);
		item.text = tileSet.getName();
		item.control = tilePicker;
		folder.selection = item;					
	}
} as Listener)

new MenuItem(fileMenu, SWT.SEPARATOR)

def newMap = new MenuItem(fileMenu, SWT.PUSH)
newMap.text = 'New Map'
newMap.addListener(SWT.Selection, {
	def rpgMap = null
	if (mapEditor?.map) {
		def warningDialog = new WarningDialog(shell)
		if (warningDialog.getResponse("This will replace the current map!")) {
			rpgMap = RpgMap.newRpgMap()
		}
	}
	else {
		rpgMap = RpgMap.newRpgMap()
	}
	if (rpgMap) mapEditor.setMap(rpgMap)
} as Listener)

def openMap = new MenuItem(fileMenu, SWT.PUSH)
openMap.text = 'Open Map'
openMap.addListener(SWT.Selection, {
	def rpgMap = null;
	if (mapEditor?.map) {
		def warningDialog = new WarningDialog(shell)
		if (warningDialog.getResponse("This will replace the current map!")) {
			rpgMap = RpgMap.loadRpgMap()
		}
	}
	else {
		rpgMap = RpgMap.loadRpgMap()
	}
	if (rpgMap) mapEditor.setMap(rpgMap)					
} as Listener)

def saveMap = new MenuItem(fileMenu, SWT.PUSH)
saveMap.text = 'Save Map'
saveMap.addListener(SWT.Selection, {
	def map = mapEditor?.map
	if (map) map.saveRpgMap()
} as Listener)

def saveMapAs = new MenuItem(fileMenu, SWT.PUSH)
saveMapAs.text = 'Save Map As'
saveMapAs.addListener(SWT.Selection, {
	def map = mapEditor?.map
	if (map) map.saveRpgMap(true)
} as Listener)

// == MENU LISTENER ==
	
fileMenu.addMenuListener([
    menuShown : {
		println 'menu shown'
		if (mapEditor?.map) {
			saveMap.enabled = true
			saveMapAs.enabled = true					
		}
		else {
			saveMap.enabled = false
			saveMapAs.enabled = false
		}
	},
	menuHidden : {
		println 'menu hidden'
	}] as MenuListener)
shell.setMenuBar(menuBar)

// == SASH FORM TO HOLD OTHER WIDGETS ==

def hForm = new SashForm(shell, SWT.HORIZONTAL | SWT.SMOOTH)
hForm.layoutData = new GridData(SWT.FILL, SWT.FILL, true, true)
hForm.sashWidth = 5

def vForm = new SashForm(hForm, SWT.VERTICAL | SWT.SMOOTH)
vForm.layoutData = new GridData(SWT.FILL, SWT.FILL, true, true)
vForm.sashWidth = 5

folder = new CTabFolder(vForm, SWT.BORDER | SWT.RESIZE)
folder.layoutData = new GridData(SWT.FILL, SWT.FILL, true, true)
folder.simple = false
folder.selectionBackground = new Color(display, TAB_COLOUR)

//recentTiles = new Button(vForm, SWT.PUSH)
recentTiles = new GRecentTiles(vForm, SWT.BORDER);
recentTiles.layoutData = new GridData(SWT.FILL, SWT.FILL, true, true);

vForm.weights = [4, 1] as int[];

mapEditor = new GMapEditor(hForm, SWT.BORDER);

hForm.weights = [4, 6] as int[];

shell.setSize(1024, 640)
shell.open()

while (!shell.disposed) {
    if (!display.readAndDispatch()) shell.display.sleep()
}

}
catch (Exception e) {
	e.printStackTrace()
}
