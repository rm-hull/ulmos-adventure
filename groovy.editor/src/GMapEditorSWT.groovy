import rpg.editor.*
import rpg.editor.core.*
import rpg.editor.model.*
import org.eclipse.swt.*
import org.eclipse.swt.custom.*
import org.eclipse.swt.events.*
import org.eclipse.swt.graphics.*
import org.eclipse.swt.layout.*
import org.eclipse.swt.widgets.*

/**
 * MapEditor is the main component in the application.  It allows users to add
 * selected tiles to a map and build up the map that will feature in the game.
 * This class also facilitates editing the information (eg. level data) required
 * by the game engine.
 * 
 * @author seldred
 */
public class GMapEditor extends Composite {
	
	def canvasHolder
    def mapEditorCanvas

	public GMapEditor(parent, style = SWT.NONE) {		
		super(parent, style)
		
		// layout setup
		layout = new GridLayout()
		layoutData = new GridData(SWT.FILL, SWT.FILL, true, true)
		
	    // radio buttons
	    def radioGroup = new Group(this, SWT.SHADOW_ETCHED_IN)
		radioGroup.layoutData = new GridData(SWT.CENTER, SWT.CENTER, true, false)
	    radioGroup.layout = new RowLayout()
	    def addButton = new Button(radioGroup, SWT.RADIO)
	    addButton.text = 'Add'
	    addButton.selection = true
	    def insertButton = new Button(radioGroup, SWT.RADIO)
	    insertButton.text = 'Insert'
	    insertButton.selection = false
	    def noneButton = new Button(radioGroup, SWT.RADIO)
	    noneButton.text = 'None'
	    noneButton.selection = false
		
		// canvas
	    canvasHolder = new ScrolledComposite(this, SWT.H_SCROLL | SWT.V_SCROLL | SWT.BORDER)
	    canvasHolder.layoutData = new GridData(SWT.FILL, SWT.FILL, true, true);
		mapEditorCanvas = new GMapEditorCanvas(canvasHolder)
		canvasHolder.content = mapEditorCanvas
		canvasHolder.expandHorizontal = true
		canvasHolder.expandVertical = true

		// label
		def tileLabel = new Label(this, SWT.CENTER)
		tileLabel.text = Constants.NO_SELECTION_LABEL
		tileLabel.layoutData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		mapEditorCanvas.tileLabel = tileLabel

		// listeners
		addButton.addListener(SWT.Selection, {
			mapEditorCanvas.editMode = GEditMode.ADD
		} as Listener)
		insertButton.addListener(SWT.Selection, {
			mapEditorCanvas.editMode = GEditMode.INSERT
		} as Listener)
		noneButton.addListener(SWT.Selection, {
			mapEditorCanvas.editMode = GEditMode.NONE
		} as Listener)
	}
	
	public void setMap(map) {
		mapEditorCanvas.map = map
		mapEditorCanvas.tileImage = map.mapImage
		Rectangle rect = map.mapImage.bounds;
		canvasHolder.setMinSize(rect.width, rect.height)
		mapEditorCanvas.redraw()
	}
	
	public RpgMap getMap() {
		return mapEditorCanvas.map
	}
}	

class GMapEditorCanvas extends TileCanvas {

	def static final String SEND_TO_BACK = "Send To Back"
	def static final String EDIT_IMAGES = "Edit Images"
	def static final String EDIT_LEVELS = "Edit Levels"
	def static final String EDIT_MASKS = "Edit Masks"
	def static final String KEEP_TOP = "Keep Top"
	def static final String CLEAR = "Clear"
	
	def tileSelection = SharedTileSelection.getInstance()
    def editMode = GEditMode.ADD
    def tileLabel
	def map

	def startTile
	def dragTile
	
	def editImagesFactory = {parent, mapTile ->
		return new TileImagesEditor(parent, mapTile);
	} as TileEditorFactory
	
	def editLevelsFactory = {parent, mapTile ->
		return new TileLevelsEditor(parent, mapTile);
	} as TileEditorFactory
	
	def editMasksFactory = {parent, mapTile ->
		return new TileMasksEditor(parent, mapTile);
	} as TileEditorFactory
	
	public GMapEditorCanvas(parent) {
		super(parent)
		
		// popup menu
		Menu popupMenu = new Menu(this)
		populatePopupMenu(popupMenu)
		menu = popupMenu
		popupMenu.addMenuListener([
		    menuShown : {
				Set<String> toEnable = new HashSet<String>()
				if (highlightTile) {
					def mapTile = map.getMapTile(highlightTile)
					int tileDepth = mapTile.tileDepth
					if (tileDepth) {
						toEnable << CLEAR
						toEnable << EDIT_IMAGES
						toEnable << EDIT_LEVELS
						toEnable << EDIT_MASKS
						if (tileDepth > 1) {
							toEnable << SEND_TO_BACK
							toEnable << KEEP_TOP
						}
					}
				}
				enableMenuItems(popupMenu, toEnable)
			},
			menuHidden: { }
		] as MenuListener)
		
		// mouse listener
		addMouseListener([
		    mouseDown : {
				if (highlightTile && it.button == 1) {
					startTile = highlightTile
				}
			},
		    mouseUp : {
				if ((highlightTile == startTile) && (it.button == 1)) {
					if (tileSelection.tileSelected) {
						Tile tile = tileSelection.getSelectedTile()
						if (editMode == GEditMode.ADD) {
							map.addTile(highlightTile, tile)
						}
						else if (editMode == GEditMode.INSERT) {
							map.insertTile(highlightTile, tile)
						}
						redraw()
						setLabelText()
					}
				}
				startTile = null
			},
		    mouseDoubleClick : { }
		] as MouseListener)
		
		// ** mouse move listener **
		addMouseMoveListener({
			if (tileImage != null) {
				if (startTile) {
					def previousDragTile = dragTile;
					dragTile = determineCurrentTile(it);
					if (dragTile != previousDragTile) {
						// work out max x and y
						def minX = Math.min(startTile.x, dragTile.x)
						def minY = Math.min(startTile.y, dragTile.y)
						def maxX = Math.max(startTile.x, dragTile.x)
						def maxY = Math.max(startTile.y, dragTile.y)
						def rows = maxY - minY + 1
						def cols = maxX - minX + 1
						ImageHelper.getSelectedImage(viewSize)
						println "$startTile -> $dragTile"
					}
				}
				else {
					dragTile = null
					Point previousHighlightTile = highlightTile;
					highlightTile = determineCurrentTile(it);
					if (highlightTile != previousHighlightTile) {
						redraw();
						setLabelText();
					}					
				}
			}
		} as MouseMoveListener)
	}
	
	public void setLabelText() {
		if (highlightTile) {
			MapTile mapTile = map.getMapTile(highlightTile)			
			tileLabel.text = highlightTile.x + Constants.LABEL_COMMA +
					highlightTile.y + Constants.SEPARATOR + mapTile.getLabel();
		}
		else {
			tileLabel.setText(Constants.NO_SELECTION_LABEL)
		}
	}
	
	private void populatePopupMenu(menu) {
		// dynamic options
		MenuItem sendToBack = new MenuItem(menu, SWT.PUSH)
		sendToBack.setText(SEND_TO_BACK)
		sendToBack.addListener(SWT.Selection, {
			map.sendToBack(highlightTile);
			redraw();
		} as Listener)
		MenuItem keepTop = new MenuItem(menu, SWT.PUSH)
		keepTop.setText(KEEP_TOP)
		keepTop.addListener(SWT.Selection, {
			map.keepTop(highlightTile);
			redraw()
			setLabelText()
		} as Listener)
		MenuItem clear = new MenuItem(menu, SWT.PUSH)
		clear.setText(CLEAR)
		clear.addListener(SWT.Selection, {
			map.clear(highlightTile)
			redraw()
			setLabelText()
		} as Listener)
		
		// separator
		new MenuItem(menu, SWT.SEPARATOR)
		
		// edit options
		MenuItem editImages = new MenuItem(menu, SWT.PUSH)
		editImages.setText(EDIT_IMAGES)
		editImages.addListener(SWT.Selection, {
			def mapTile = map.getMapTile(highlightTile)
			def tileEditor = new GTileEditDialog(DisplayHelper.getShell(), editImagesFactory);
			tileEditor.editTile(mapTile);
			setLabelText()
			// update the map image
			map.updateTileImage(mapTile, highlightTile)
			redraw()
		} as Listener)
		MenuItem editLevels = new MenuItem(menu, SWT.PUSH)
		editLevels.setText(EDIT_LEVELS)
		editLevels.addListener(SWT.Selection, {
			def mapTile = map.getMapTile(highlightTile)
			def tileEditor = new GTileEditDialog(DisplayHelper.getShell(), editLevelsFactory, 240, 320);
			tileEditor.editTile(mapTile);
			setLabelText()
		} as Listener)
		MenuItem editMasks = new MenuItem(menu, SWT.PUSH)
		editMasks.setText(EDIT_MASKS)
		editMasks.addListener(SWT.Selection, {
			def mapTile = map.getMapTile(highlightTile)
			def tileEditor = new GTileEditDialog(DisplayHelper.getShell(), editMasksFactory);
			tileEditor.editTile(mapTile);
			setLabelText()
		} as Listener)
	}
			
	private void enableMenuItems(menu, toEnable) {
		for (item in menu.items) {
			if ((item.style == SWT.PUSH) && (item.text in toEnable)) {
				item.enabled = true
			}
			else {
				item.enabled = false
			}
		}
	}
}

enum GEditMode {
	ADD, INSERT, NONE;
}

try {

def display = DisplayHelper.getDisplay();
def shell = DisplayHelper.getShell();
shell.layout = new GridLayout();
		
def mapEditor = new GMapEditor(shell);
mapEditor.mapEditorCanvas.tileSelection = TileSelectionStub.getInstance();
def rpgMap = RpgMap.newRpgMap();
mapEditor.setMap(rpgMap);
		
shell.setSize(600, 600);
shell.open();
while (!shell.disposed) {
    if (!display.readAndDispatch()) shell.display.sleep()
}

}
catch (Exception e) {
	e.printStackTrace()
}