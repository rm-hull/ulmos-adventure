package rpg.editor.components;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;

import rpg.editor.Constants;
import rpg.editor.model.Tile;

/**
 * Component that displays the last 10 tiles and allows the user to pick from
 * them as they can with the regular tile picker.

 * This class also implements the TileSelection interface itself and acts as a proxy
 * between the TilePicker and the SharedTileSelection.
 * 
 * @author seldred
 */
public class RecentTiles extends Composite implements TileSelection {
	
	private static final int MAX_TILES = 10;
	
    private TileSelection tileSelection = SharedTileSelection.getInstance();
	
    private ScrolledComposite canvasHolder;
    private Label tileLabel;
    
    private List<Tile> tiles = new ArrayList<Tile>();
    
    private MyTilePickerCanvas tilePickerCanvas;
    
	public RecentTiles(Composite parent) {
		this(parent, SWT.NONE);
	}

	public RecentTiles(Composite parent, int style) {

		super(parent, style);
		
		// layout setup
		setLayout(new GridLayout());
		setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		// canvas
	    canvasHolder = new ScrolledComposite(this, SWT.H_SCROLL | SWT.V_SCROLL | SWT.BORDER);
	    canvasHolder.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		tilePickerCanvas = new MyTilePickerCanvas(canvasHolder);
		canvasHolder.setContent(tilePickerCanvas);
		canvasHolder.setExpandHorizontal(true);
		canvasHolder.setExpandVertical(true);
		
		// label
		tileLabel = new Label(this, SWT.CENTER);
		tileLabel.setText(Constants.NO_SELECTION_LABEL);
		tileLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}
	
	public void tileSelected(Tile tile) {
		// add to the list of tiles
		tiles.add(tile);
		if (tiles.size() > MAX_TILES) {
			// tiles.remove(0).dispose();
			tiles.remove(0);
		}
		tilePickerCanvas.selectedTile = new Point(tiles.size() - 1, 0);
		// update other components
		tileSelection.tileSelected(tile);
		tilePickerCanvas.updateTileImage();	
	}
	
	private class MyTilePickerCanvas extends TilePickerCanvas {

		public MyTilePickerCanvas(Composite parent) {
			super(parent);
		}
		
		@Override
		public boolean isSelectionValid(Point tilePoint) {
			return true;
		}

		@Override
		public void tileSelectedAction() {
			tileSelection.tileSelected(tiles.get(selectedTile.x));
		}

		@Override
		public void setLabelText() {
			if (highlightTile.equals(NO_SELECTION)) {
				tileLabel.setText(Constants.NO_SELECTION_LABEL);
			}
			else {
				tileLabel.setText(tiles.get(highlightTile.x).getName());
			}
		}
		
		public void updateTileImage() {
			if (tileImage != null) {
				tileImage.dispose();
			}
			tileImage = new Image(DisplayHelper.getDisplay(),
					tiles.size() * viewSize.getTileSize(), viewSize.getTileSize());
			GC gc = new GC(tileImage);
			int i = 0;
			for (Tile tile: tiles) {
				gc.drawImage(tile.getImage(), i * viewSize.getTileSize(), 0);
				i++;
			}
			gc.dispose();
			Rectangle rect = tileImage.getBounds();
			canvasHolder.setMinSize(rect.width, rect.height);
			redraw();
		}
	}

	public Tile getSelectedTile() {
		// TODO Auto-generated method stub
		return null;
	}

	public boolean isTileSelected() {
		// TODO Auto-generated method stub
		return false;
	}
	
	/*@Override
	public void dispose() {
		super.dispose();
		for (Image image: tileImages.values()) {
			image.dispose();
		}
	}*/
}
