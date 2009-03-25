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
	    def replaceButton = new Button(radioGroup, SWT.RADIO)
		replaceButton.text = 'Replace'
		replaceButton.selection = false
	    def editButton = new Button(radioGroup, SWT.RADIO)
		editButton.text = 'Edit'
		editButton.selection = false
		
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
		replaceButton.addListener(SWT.Selection, {
			mapEditorCanvas.editMode = GEditMode.REPLACE
		} as Listener)
		editButton.addListener(SWT.Selection, {
			mapEditorCanvas.editMode = GEditMode.EDIT
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
				preparePopupMenu(popupMenu)
			},
			menuHidden: { }
		] as MenuListener)
		
		// ** mouse listener **
		addMouseListener([
		    mouseDown : {
				if ((it.button == 1) && highlightTile) {
					startTile = highlightTile
					highlightRectangle = new Rectangle(highlightTile.x, highlightTile.y, 1, 1)
				}
			},
		    mouseUp : {
				if ((it.button == 1) && highlightRectangle) {
					startTile = null
					if (tileSelection.tileSelected) {
						Tile tile = tileSelection.getSelectedTile()
						if (editMode == GEditMode.ADD) {							map.addTile(determineTilePoints(), tile)						}
						else if (editMode == GEditMode.REPLACE) {
							map.insertTile(determineTilePoints(), tile)
						}
						redraw()
						setLabelText()
					}						
				}
			},
		    mouseDoubleClick : { }
		] as MouseListener)
		
		// ** mouse move listener **
		addMouseMoveListener({
			if (tileImage) {
				def previousHighlightTile = highlightTile;
				highlightTile = determineTilePoint(it);
				if (startTile) {
					// if we have a start tile then we know that the mouse button is
					// down, ie. the user is changing the selected area on the map
					if (highlightTile != previousHighlightTile) {
						if (highlightTile) {
							highlightRectangle = determineTileRectangle()
							redraw();
						}
						setLabelText();
					}
				}
				else {
					// otherwise they're just moving the mouse around the map
					if (highlightTile != previousHighlightTile) {
						highlightRectangle = null
						redraw();
						setLabelText();
					}					
				}
			}
		} as MouseMoveListener)
	}
	
	def void setLabelText() {
		if (highlightTile) {
			MapTile mapTile = map.getMapTile(highlightTile)			
			tileLabel.text = highlightTile.x + Constants.LABEL_COMMA +
					highlightTile.y + Constants.SEPARATOR + mapTile.getLabel();
		}
		else {
			tileLabel.setText(Constants.NO_SELECTION_LABEL)
		}
	}

	def preparePopupMenu(popupMenu) {
		def toEnable = [] as Set
		if (highlightTile) {
			if (!highlightRectangle) {
				highlightRectangle = new Rectangle(highlightTile.x, highlightTile.y, 1, 1)
			}
			def tilePoints = determineTilePoints()
			def selected = tilePoints.size()
			tilePoints.each {
				def mapTile = map.getMapTile(it)
				int tileDepth = mapTile.tileDepth
				if (tileDepth) {
					toEnable << CLEAR
					if (tileDepth > 1) {
						toEnable << SEND_TO_BACK
						toEnable << KEEP_TOP
					}
					// some options are only available on single tiles
					if (selected == 1) {
						toEnable << EDIT_IMAGES
						toEnable << EDIT_MASKS
					}
				}
				else if (mapTile.levels) {
					toEnable << CLEAR					
				}
			}
			toEnable << EDIT_LEVELS
		}
		enableMenuItems(popupMenu, toEnable)
	}
	
	def determineTileRectangle() {
		def minX = Math.min(startTile.x, highlightTile.x)
		def minY = Math.min(startTile.y, highlightTile.y)
		def maxX = Math.max(startTile.x, highlightTile.x)
		def maxY = Math.max(startTile.y, highlightTile.y)
		return new Rectangle(minX, minY, 
				maxX - minX + 1, maxY - minY + 1)
	}
	
    def determineTilePoints() {
    	def tilePoints = new ArrayList<Point>();
    	highlightRectangle.x.upto(highlightRectangle.x + highlightRectangle.width - 1) { x ->
    		highlightRectangle.y.upto(highlightRectangle.y + highlightRectangle.height - 1) { y ->
				tilePoints << new Point(x, y);
    		}
    	}
    	return tilePoints;
    }

	def populatePopupMenu(menu) {
		// dynamic options
		MenuItem sendToBack = new MenuItem(menu, SWT.PUSH)
		sendToBack.setText(SEND_TO_BACK)
		sendToBack.addListener(SWT.Selection, {
			map.sendToBack(determineTilePoints());
			redraw();
		} as Listener)
		MenuItem keepTop = new MenuItem(menu, SWT.PUSH)
		keepTop.setText(KEEP_TOP)
		keepTop.addListener(SWT.Selection, {
			map.keepTop(determineTilePoints());
			redraw()
			setLabelText()
		} as Listener)
		MenuItem clear = new MenuItem(menu, SWT.PUSH)
		clear.setText(CLEAR)
		clear.addListener(SWT.Selection, {
			map.clear(determineTilePoints())
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
			def tileEditor = new GTileEditDialog(DisplayHelper.getShell(), editImagesFactory)
			if (tileEditor.editTile(mapTile)) {
				setLabelText()
				// update the map image
				map.updateTileImage(mapTile, highlightTile)
				redraw()
			}
		} as Listener)
		MenuItem editLevels = new MenuItem(menu, SWT.PUSH)
		editLevels.setText(EDIT_LEVELS)
		editLevels.addListener(SWT.Selection, {
			def mapTile = map.getMapTile(highlightTile)
			def tileEditor = new GTileEditDialog(DisplayHelper.getShell(), editLevelsFactory, 240, 320)
			if (tileEditor.editTile(mapTile)) {
				// edit levels can be applied to a range of tiles
				determineTilePoints().each {
					map.getMapTile(it).setLevels(mapTile.getLevels())
				}
				setLabelText()				
			}
		} as Listener)
		MenuItem editMasks = new MenuItem(menu, SWT.PUSH)
		editMasks.setText(EDIT_MASKS)
		editMasks.addListener(SWT.Selection, {
			def mapTile = map.getMapTile(highlightTile)
			def tileEditor = new GTileEditDialog(DisplayHelper.getShell(), editMasksFactory)
			if (tileEditor.editTile(mapTile)) {
				setLabelText()				
			}
		} as Listener)
	}
			
	def enableMenuItems(menu, toEnable) {
		menu.items.each {
			if ((it.style == SWT.PUSH) && (it.text in toEnable)) {
				it.enabled = true
			}
			else {
				it.enabled = false
			}
		}
	}
}

enum GEditMode {
	ADD, REPLACE, EDIT;
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