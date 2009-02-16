package rpg.editor.components;

import java.util.ArrayList;
import java.util.List;
import java.util.ListIterator;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Canvas;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Spinner;

import rpg.editor.Constants;
import rpg.editor.model.MapTile;
import rpg.editor.model.MaskTile;
import rpg.editor.model.TileSet;

public class TileMasksEditor extends TileEditor {

	private int numTiles;

	private MaskTile[] tiles;
	private Spinner[] levels;
	private Vertical[] verticals;
	
	public TileMasksEditor(Composite parent, MapTile mapTile) {
		this(parent, SWT.NONE, mapTile);
	}
	
	public TileMasksEditor(Composite parent, int style, MapTile mapTile) {
		super(parent, style, mapTile);
		
		this.setLayout(new GridLayout());
		this.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		List<MaskTile> myTiles = mapTile.getTiles();
		numTiles = myTiles.size();
		
		tiles = new MaskTile[numTiles];
		levels = new Spinner[numTiles];
		verticals = new Vertical[numTiles];
		
		ListIterator<MaskTile> iterator = myTiles.listIterator(numTiles);
		int i = 0;
		while (iterator.hasPrevious()) {
			MaskTile tile = iterator.previous();
			tiles[i] = tile;
			// create the image without transparency
			ImageData imageData = tile.getTile().getImage().getImageData();
			imageData.transparentPixel = -1;
			final Image tileImage = new Image(getDisplay(),
					imageData.scaledTo(ViewSize.LARGE.getTileSize(), ViewSize.LARGE.getTileSize()));

			Group tileRow = new Group(this, SWT.SHADOW_ETCHED_IN);
			tileRow.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
			tileRow.setLayout(new GridLayout(7, false));
			
			// now create a simple canvas for each tile 
			Canvas tileCanvas = new Canvas(tileRow, SWT.NONE);
			tileCanvas.addListener(SWT.Paint, new Listener() {
				public void handleEvent (Event e) {
					GC gc = e.gc;
					gc.drawImage(tileImage, 0, 0);
					gc.dispose();
				}		
			});
			
			// mask level
			Label label = new Label(tileRow, SWT.CENTER);
			label.setText("Mask:");
			final Button toggle = new Button(tileRow, SWT.CHECK);
			label = new Label(tileRow, SWT.CENTER);
			label.setText("Level:");			
			final Spinner level = new Spinner(tileRow, SWT.NONE);
			level.setMinimum(-10);
			level.setEnabled(false);
			levels[i] = level;
			label = new Label(tileRow, SWT.CENTER);
			label.setText("Vertical:");			
			final Button verticalToggle = new Button(tileRow, SWT.CHECK);
			verticalToggle.setEnabled(false);
			final Vertical vertical = new Vertical();
			verticals[i] = vertical;
			
			// set existing value
			String maskLevel = tile.getMaskLevel();
			if (maskLevel != null) {
				toggle.setSelection(true);
				// int maskLevel = maskLevels.get(key);
				if (maskLevel.startsWith(Constants.VERTICAL)) {
					vertical.flag = true;
					verticalToggle.setSelection(true);
					maskLevel = maskLevel.substring(1);
				}
				level.setSelection(Integer.parseInt(maskLevel));
				level.setEnabled(true);
				verticalToggle.setEnabled(true);
			}
			
			// add listener
			toggle.addListener(SWT.Selection, new Listener() {
				public void handleEvent(Event event) {
					if (toggle.getSelection() == true) {
						level.setEnabled(true);
						verticalToggle.setEnabled(true);
					}
					else {
						level.setEnabled(false);
						verticalToggle.setEnabled(false);
					}
				}
			});
			
			verticalToggle.addListener(SWT.Selection, new Listener() {
				public void handleEvent(Event event) {
					vertical.flag = !vertical.flag;
				}
			});

			i++;
		}
	}
	
	@Override
	public void applyChanges() {
		List<MaskTile> myTiles = new ArrayList<MaskTile>();
		for (int i = numTiles - 1; i >= 0; i--) {
			MaskTile tile = tiles[i];
			Spinner level = levels[i];
			if (level.isEnabled()) {
				if (verticals[i].flag) {
					tile.setMaskLevel(Constants.VERTICAL + level.getSelection());
				}
				else {
					tile.setMaskLevel(Constants.EMPTY + level.getSelection());					
				}
			}
			else {
				tile.setMaskLevel(null);
			}
			myTiles.add(tile);
		}
		getMapTile().setTiles(myTiles);
	}
	
	private class Vertical {
		protected boolean flag = false;
	}

	// =====================================================
	// == main method to test this component in isolation ==
	// =====================================================
	
	public static void main(String[] args) {		

		try {
		Display display = DisplayHelper.getDisplay();
		Shell shell = DisplayHelper.getShell();
		shell.setLayout(new GridLayout());
		
		TileConversion tileConversion = TileSelectionStub.getInstance();
		MapTile mapTile = new MapTile(null);
		TileSet tileSet = TileSet.loadTileSet("grass");
		mapTile.addTile(tileConversion.convertTile(tileSet.getTile("n1")));
		mapTile.addTile(tileConversion.convertTile(tileSet.getTile("n2")));
		tileSet = TileSet.loadTileSet("wood");
		mapTile.addTile(tileConversion.convertTile(tileSet.getTile("c_supp")), "V2");
		mapTile.addTile(tileConversion.convertTile(tileSet.getTile("l_supp")), "3");
		mapTile.setLevels(new String[] { "1", "S3", "2" });
		
		new TileMasksEditor(shell, mapTile);
		
		shell.pack();
		shell.open();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) display.sleep();
		}
		
		// dispose resources
		ImageHelper.dispose();
		display.dispose();
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}
}
