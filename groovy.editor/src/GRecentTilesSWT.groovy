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
 * Component that displays the last 10 tiles and allows the user to pick from
 * them as they can with the regular tile picker.

 * This class also implements the TileSelection interface itself and acts as a proxy
 * between the TilePicker and the SharedTileSelection.
 * 
 * @author seldred
 */
public class GRecentTiles extends Composite implements TileSelection {
	
    def canvasHolder;
    def recentTilesCanvas;

	public GRecentTiles(parent, style = SWT.NONE) {
		super(parent, style)
		
		// layout setup
		layout = new GridLayout()
		layoutData = new GridData(SWT.FILL, SWT.FILL, true, true)
		
		// canvas
	    canvasHolder = new ScrolledComposite(this, SWT.H_SCROLL | SWT.V_SCROLL | SWT.BORDER)
	    canvasHolder.layoutData = new GridData(SWT.FILL, SWT.FILL, true, true)		try {
		recentTilesCanvas = new GRecentTilesCanvas(canvasHolder)		}		catch (Exception e) {			e.printStackTrace()		}
		canvasHolder.content = recentTilesCanvas
		canvasHolder.expandHorizontal = true
		canvasHolder.expandVertical = true
		
		// label
		def tileLabel = new Label(this, SWT.CENTER)
		tileLabel.text = Constants.NO_SELECTION_LABEL
		tileLabel.layoutData = new GridData(SWT.FILL, SWT.CENTER, true, false)		recentTilesCanvas.tileLabel = tileLabel
	}
	
	public void tileSelected(Tile tile) {
		def rect = recentTilesCanvas.tileSelected(tile)
		canvasHolder.setMinSize(rect.width, rect.height);		recentTilesCanvas.redraw();	}
	
	public Tile getSelectedTile() {
		return null;
	}

	public boolean isTileSelected() {
		return false;
	}
}

class GRecentTilesCanvas extends TilePickerCanvas {

    def static final MAX_TILES = 10
	
    def tileSelection = SharedTileSelection.getInstance()	    def tileLabel
    
    def tiles = new ArrayList<Tile>()
    
	public GRecentTilesCanvas(parent) {		super(parent)	}
	
	public boolean isSelectionValid(Point tilePoint) {
		return true
	}

	public void tileSelectedAction() {
		tileSelection.tileSelected(tiles.get(selectedTile.x))
	}

	public void setLabelText() {
		if (highlightTile) {
			tileLabel.text = tiles.get(highlightTile.x).getName()
		}
		else {
			tileLabel.text = Constants.NO_SELECTION_LABEL
		}
	}
	
	public Rectangle tileSelected(tile) {		// pass through to tile selection		tileSelection.tileSelected(tile)		// add to the list of tiles
		tiles.add(tile)
		if (tiles.size() > MAX_TILES) {
			tiles.remove(0)
		}
		// update tile image
		selectedTile = new Point(tiles.size() - 1, 0)
		return updateTileImage()
	}
	
	public Rectangle updateTileImage() {
		if (tileImage) {
			tileImage.dispose()
		}
		tileImage = new Image(DisplayHelper.display,
				tiles.size() * viewSize.tileSize, viewSize.tileSize)
		def gc = new GC(tileImage)
		int i = 0
		for (tile in tiles) {
			gc.drawImage(tile.image, i * viewSize.tileSize, 0)
			i++
		}
		gc.dispose()
		return tileImage.bounds
	}
}
