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
 * Component that allows the user to pick a tile from a TileSet.
 * 
 * @author seldred
 */
public class GTilePicker extends Composite {
	
    def canvasHolder
    def tilePickerCanvas
    
	public GTilePicker(parent, tileSet, style = SWT.NONE) {
		super(parent, style)
				
		// layout setup
		layout = new GridLayout()
		layoutData = new GridData(SWT.FILL, SWT.FILL, true, true)
		
	    // radio buttons
	    def radioGroup = new Group(this, SWT.SHADOW_ETCHED_IN)
		radioGroup.layoutData = new GridData(SWT.CENTER, SWT.CENTER, true, false)
	    radioGroup.layout = new RowLayout()
		def smallButton = new Button(radioGroup, SWT.RADIO)
		smallButton.text = ViewSize.SMALL.getLabel()
		smallButton.selection = false
		def mediumButton = new Button(radioGroup, SWT.RADIO)
		mediumButton.text = ViewSize.MEDIUM.getLabel()
		mediumButton.selection = true
		def largeButton = new Button(radioGroup, SWT.RADIO)
		largeButton.text = ViewSize.LARGE.getLabel()
		largeButton.setSelection(false)

		// canvas
	    canvasHolder = new ScrolledComposite(this, SWT.H_SCROLL | SWT.V_SCROLL | SWT.BORDER)
	    canvasHolder.layoutData = new GridData(SWT.FILL, SWT.FILL, true, true)
		tilePickerCanvas = new GTilePickerCanvas(canvasHolder)
		tilePickerCanvas.tileSet = tileSet
		tilePickerCanvas.tileImage = tileSet.getTilesImage(ViewSize.MEDIUM)
		canvasHolder.content = tilePickerCanvas
		canvasHolder.expandHorizontal = true
		canvasHolder.expandVertical = true
		Rectangle rect = tilePickerCanvas.tileImage.bounds
		canvasHolder.setMinSize(rect.width, rect.height)
		
		// label
		def tileLabel = new Label(this, SWT.CENTER)
		tileLabel.text = Constants.NO_SELECTION_LABEL
		tileLabel.layoutData = new GridData(SWT.FILL, SWT.CENTER, true, false)
		tilePickerCanvas.tileLabel = tileLabel

		// listeners
		smallButton.addListener(SWT.Selection, {
			setViewSize(ViewSize.SMALL)
		} as Listener)
		mediumButton.addListener(SWT.Selection, {
			setViewSize(ViewSize.MEDIUM)
		} as Listener)
		largeButton.addListener(SWT.Selection, {			setViewSize(ViewSize.LARGE)		} as Listener)
	}

	public void setViewSize(viewSize) {
		tilePickerCanvas.viewSize = myViewSize
		tilePickerCanvas.tileImage = tileSet.getTilesImage(myViewSize)
		Rectangle rect = tilePickerCanvas.tileImage.bounds
		canvasHolder.setMinSize(rect.width, rect.height)
		tilePickerCanvas.redraw()
	}

	public void setTileSelection(tileSelection) {
		tilePickerCanvas.tileSelection = tileSelection
	}
	
	public void dispose() {
		super.dispose()
		tileSet.dispose()
	}
}

class GTilePickerCanvas extends TilePickerCanvas {

	def tileSelection
	def tileSet
    def tileLabel

	public GTilePickerCanvas(parent) {
		super(parent)
	}
			
	public boolean isSelectionValid(Point tilePoint) {
		if (tileSet.getTile(tilePoint)) {
			return true
		}
		return false
	}

	public void tileSelectedAction() {
		tileSelection.tileSelected(tileSet.getTile(selectedTile))
	}

	public void setLabelText() {
		def labelText = Constants.NO_SELECTION_LABEL
		if (highlightTile) {
			Tile tile = tileSet.getTile(highlightTile)
			if (tile) {
				labelText = highlightTile.x + Constants.LABEL_COMMA + 
						highlightTile.y + Constants.SEPARATOR + tile.getName()					
			}
		}
		tileLabel.text = labelText
	}
}

def display = DisplayHelper.getDisplay();
def shell = DisplayHelper.getShell();
shell.setLayout(new GridLayout());
		
def tileSet = TileSet.loadTileSet();
def tilePicker = new GTilePicker(shell, tileSet);
tilePicker.setTileSelection(TileSelectionStub.getInstance());
					
shell.setSize(800, 400);
shell.open();
while (!shell.disposed) {
    if (!display.readAndDispatch()) shell.display.sleep()
}
