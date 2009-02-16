package rpg.editor.components;

import java.util.ArrayList;
import java.util.List;

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
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableItem;

import rpg.editor.model.MapTile;
import rpg.editor.model.MaskTile;
import rpg.editor.model.TileSet;

public class TileImagesEditor extends TileEditor {
	
	private Table tileTable;
	private Canvas flatTileCanvas;
	
	public TileImagesEditor(Composite parent, MapTile mapTile) {
		this(parent, SWT.NONE, mapTile);
	}
	
	public TileImagesEditor(Composite parent, int style, MapTile mapTile) {
		super(parent, style, mapTile);
		
		this.setLayout(new GridLayout(2, false));
		this.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		List<MaskTile> myTiles = mapTile.getTiles();
		
		int numTiles = myTiles.size();		
		final Image[] transparentTileImages = new Image[numTiles];
		Image[] tileImages = new Image[numTiles];
		
		int i = 0;
		for (MaskTile tile: myTiles) {
			// create the image with transparency
			ImageData imageData = tile.getTile().getImage().getImageData();
			transparentTileImages[i] = new Image(getDisplay(),
					imageData.scaledTo(ViewSize.LARGE.getTileSize(), ViewSize.LARGE.getTileSize()));			
			// create the image without transparency
			imageData.transparentPixel = -1;
			tileImages[i] = new Image(getDisplay(),
					imageData.scaledTo(ViewSize.LARGE.getTileSize(), ViewSize.LARGE.getTileSize()));
			i++;
		}

		// tile widgets
		createTileHolder(tileImages);
		
		// flattened tile
		flatTileCanvas = new Canvas(this, SWT.NONE);
		flatTileCanvas.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, true));
		flatTileCanvas.addListener(SWT.Paint, new Listener() {
			public void handleEvent (Event e) {
				int[] indices = extractIndices();
				GC gc = e.gc;
				for (int i: indices) {
					gc.drawImage(transparentTileImages[i], 0, 0);						
				}
				gc.dispose();
			}
		});
	}
	
	private int[] extractIndices() {
		int numItems = tileTable.getItemCount();
		int[] indices = new int[numItems];
		int i = numItems;
		for (TableItem item: tileTable.getItems()) {
			i--;
			indices[i] = ((Integer)item.getData()).intValue();
		}
		return indices;
	}
	
	private void createTileHolder(Image[] tileImages) {
		Group tileHolder = new Group(this, SWT.SHADOW_ETCHED_IN);
		tileHolder.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		tileHolder.setLayout(new GridLayout(2, false));

		tileTable = new Table(tileHolder, SWT.SINGLE);
		tileTable.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		tileTable.setLinesVisible(true);
		for (int i = tileImages.length - 1; i >= 0; i--) {
			TableItem item = new TableItem(tileTable, SWT.NONE);
			item.setImage(tileImages[i]);
			item.setText("Index: " + i);
			item.setData(i);
		}
		
		Composite buttons = new Composite(tileHolder, SWT.NONE);
		buttons.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));
		buttons.setLayout(new GridLayout());
		final Button up = new Button(buttons, SWT.PUSH);
		up.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));
		up.setText("Up");
		up.setEnabled(false);
		up.addListener(SWT.Selection, new ShiftTileListener(ShiftUnit.UP));
		// down button
		final Button down = new Button(buttons, SWT.PUSH);
		down.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));
		down.setText("Down");
		down.setEnabled(false);
		down.addListener(SWT.Selection, new ShiftTileListener(ShiftUnit.DOWN));
		// delete button
		final Button delete = new Button(buttons, SWT.PUSH);
		delete.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));
		delete.setText("Delete");
		delete.setEnabled(false);
		delete.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				tileTable.remove(tileTable.getSelectionIndex());
				// update other components
				tileTable.deselectAll();
				tileTable.notifyListeners(SWT.Selection, null);
				flatTileCanvas.redraw();
			}			
		});

		tileTable.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				// enable / disable buttons based on which item is selected
				int currentSelection = tileTable.getSelectionIndex();
				if (currentSelection == -1) {
					// nothing selected
					up.setEnabled(false);
					down.setEnabled(false);
					delete.setEnabled(false);
				}
				else {
					// something selected
					boolean enableUp = true, enableDown = true;
					if (currentSelection == 0) {
						enableUp = false;
					}
					if (currentSelection == tileTable.getItemCount() - 1) {
						enableDown = false;
					}
					up.setEnabled(enableUp);
					down.setEnabled(enableDown);
					delete.setEnabled(true);
				}	
			}
		});
	}
	
	private enum ShiftUnit {
		
		UP(-1), DOWN(1);
		
		private int amount;
		
		private ShiftUnit(int myAmount) {
			amount = myAmount;
		}
	}
	
	// shifts tile images up/down depending on the shift unit
	private class ShiftTileListener implements Listener {

		private ShiftUnit shiftUnit;
		
		public ShiftTileListener(ShiftUnit myShift) {
			shiftUnit = myShift;
		}

		public void handleEvent(Event event) {
			// it appears there is no way to swap items in a table - therefore,
			// we have to swap the contents of the items
			int selectedIndex = tileTable.getSelectionIndex();
			int shiftedIndex = selectedIndex + shiftUnit.amount;
			TableItem selectedItem = tileTable.getItem(selectedIndex);
			Image selectedImage = selectedItem.getImage();
			String selectedText = selectedItem.getText();
			Object selectedData = selectedItem.getData();
			TableItem shiftedItem = tileTable.getItem(shiftedIndex);
			Image shiftedImage = shiftedItem.getImage();
			String shiftedText = shiftedItem.getText();
			Object shiftedData = shiftedItem.getData();
			selectedItem.setImage(shiftedImage);
			selectedItem.setText(shiftedText);
			selectedItem.setData(shiftedData);
			shiftedItem.setImage(selectedImage);
			shiftedItem.setText(selectedText);
			shiftedItem.setData(selectedData);
			// update other components
			tileTable.setSelection(shiftedIndex);
			tileTable.notifyListeners(SWT.Selection, null);
			flatTileCanvas.redraw();
		}
	}
	
	@Override
	public void applyChanges() {
		List<MaskTile> tiles = getMapTile().getTiles();
		List<MaskTile> myTiles = new ArrayList<MaskTile>();
		int[] indices = extractIndices();
		for (int i: indices) {
			myTiles.add(tiles.get(i));
		}
		getMapTile().setTiles(myTiles);
	}
	
	// =====================================================
	// == main method to test this component in isolation ==
	// =====================================================
	
	public static void main(String[] args) {		

		Display display = DisplayHelper.getDisplay();
		Shell shell = DisplayHelper.getShell();
		shell.setLayout(new GridLayout());
		
		TileConversion tileConversion = TileSelectionStub.getInstance();
		MapTile mapTile = new MapTile(null);
		TileSet tileSet = TileSet.loadTileSet("grass");
		mapTile.addTile(tileConversion.convertTile(tileSet.getTile("n1")));
		mapTile.addTile(tileConversion.convertTile(tileSet.getTile("n2")));
		tileSet = TileSet.loadTileSet("wood");
		mapTile.addTile(tileConversion.convertTile(tileSet.getTile("c_supp")), "2");
		mapTile.addTile(tileConversion.convertTile(tileSet.getTile("l_supp")));
		mapTile.setLevels(new String[] { "1", "S3", "2" });
		
		new TileImagesEditor(shell, mapTile);
		
		shell.pack();
		shell.open();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) display.sleep();
		}
		
		// dispose resources
		ImageHelper.dispose();
		display.dispose();
	}
}
