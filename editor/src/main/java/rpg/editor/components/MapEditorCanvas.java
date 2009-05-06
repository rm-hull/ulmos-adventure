package rpg.editor.components;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.MenuAdapter;
import org.eclipse.swt.events.MenuEvent;
import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.MouseMoveListener;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;

import rpg.editor.Constants;
import rpg.editor.core.DisplayHelper;
import rpg.editor.core.SharedTileSelection;
import rpg.editor.core.TileCanvas;
import rpg.editor.core.TileEditor;
import rpg.editor.core.TileEditorFactory;
import rpg.editor.core.TileImagesEditor;
import rpg.editor.core.TileLevelsEditor;
import rpg.editor.core.TileMasksEditor;
import rpg.editor.core.TileSelection;
import rpg.editor.model.MapTile;
import rpg.editor.model.RpgMap;
import rpg.editor.model.Tile;

public class MapEditorCanvas extends TileCanvas {

	private static final String SEND_TO_BACK = "Send To Back";
	private static final String KEEP_TOP = "Keep Top";
	private static final String CLEAR = "Clear";

	private static final String EDIT_IMAGES = "Edit Images";
	private static final String EDIT_LEVELS = "Edit Levels";
	private static final String EDIT_MASKS = "Edit Masks";
	
	private static final String CUT = "CUT";;
	private static final String COPY = "COPY";
	private static final String PASTE = "PASTE";
		
	protected TileSelection tileSelection = SharedTileSelection.getInstance();
	protected EditMode editMode = EditMode.ADD;
	protected Label tileLabel;
	protected RpgMap map;

	private Point startTile;

	private TileEditorFactory editImagesFactory = new TileEditorFactory() {
		public TileEditor newTileEditor(Composite parent, MapTile mapTile) {
			return new TileImagesEditor(parent, mapTile);
		}
	};
	
	private TileEditorFactory editLevelsFactory = new TileEditorFactory() {
		public TileEditor newTileEditor(Composite parent, MapTile mapTile) {
			return new TileLevelsEditor(parent, mapTile);
		}
	};

	private TileEditorFactory editMasksFactory = new TileEditorFactory() {
		public TileEditor newTileEditor(Composite parent, MapTile mapTile) {
			return new TileMasksEditor(parent, mapTile);
		}
	};

	public MapEditorCanvas(Composite parent) {
		super(parent);
		
		// popup menu
		final Menu popupMenu = new Menu(this);
		populatePopupMenu(popupMenu);
		setMenu(popupMenu);
		popupMenu.addMenuListener(new MenuAdapter() {
			@Override
			public void menuShown(MenuEvent event) {
				System.out.println("hello");
				preparePopupMenu(popupMenu);
			}
		});
		
		// mouse listener
		addMouseListener(new MouseAdapter() {
			@Override
			public void mouseDown(MouseEvent event) {
				if ((event.button == 1) && (highlightTile != null)) {
					startTile = highlightTile;
					highlightRectangle = new Rectangle(highlightTile.x, highlightTile.y, 1, 1);
				}
			}
			@Override
			public void mouseUp(MouseEvent event) {
				if ((event.button == 1) && (highlightRectangle != null)) {
					startTile = null;
					if (tileSelection.isTileSelected()) {
						Tile tile = tileSelection.getSelectedTile();
						if (editMode == EditMode.ADD) {
							map.addTile(determineTilePoints(), tile);
						}
						else if (editMode == EditMode.REPLACE) {
							map.insertTile(determineTilePoints(), tile);
						}
						redraw();
						setLabelText();
					}						
				}
			}
		});
		
		// mouse move listener
		addMouseMoveListener(new MouseMoveListener() {
			public void mouseMove(MouseEvent event) {
				if (tileImage != null) {
					Point previousHighlightTile = highlightTile;
					highlightTile = determineTilePoint(event);
					if (startTile == null) {
						// if we don't have a start tile then we know that the mouse button
						// is up, ie. the user is just moving the mouse around the map
						if (highlightTile != previousHighlightTile) {
							highlightRectangle = null;
							redraw();
							setLabelText();
						}					
					}
					else {
						// otherwise, the user is changing the selected area on the map
						if (highlightTile != previousHighlightTile) {
							if (highlightTile != null) {
								highlightRectangle = determineTileRectangle();
								redraw();
							}
							setLabelText();
						}
					}
				}
			}
		});
	}
	
	public void setLabelText() {
		if (highlightTile != null) {
			MapTile mapTile = map.getMapTile(highlightTile);			
			tileLabel.setText(highlightTile.x + Constants.LABEL_COMMA +
					highlightTile.y + Constants.SEPARATOR + mapTile.getLabel());
		}
		else {
			tileLabel.setText(Constants.NO_SELECTION_LABEL);
		}
	}

	private void preparePopupMenu(Menu popupMenu) {
		Set<String> toEnable = new HashSet<String>();
		if (highlightTile != null) {
			if (highlightRectangle == null) {
				highlightRectangle = new Rectangle(highlightTile.x, highlightTile.y, 1, 1);
			}
			List<Point> tilePoints = determineTilePoints();
			int selected = tilePoints.size();
			for (Point tilePoint: tilePoints) {
				MapTile mapTile = map.getMapTile(tilePoint);
				int tileDepth = mapTile.getTileDepth();
				if (tileDepth > 0) {
					toEnable.add(CLEAR);
					if (tileDepth > 1) {
						toEnable.add(SEND_TO_BACK);
						toEnable.add(KEEP_TOP);
					}
					// some options are only available on single tiles
					if (selected == 1) {
						toEnable.add(EDIT_IMAGES);
						toEnable.add(EDIT_MASKS);
					}
				}
				else if (mapTile.getLevels() != null) {
					toEnable.add(CLEAR);			
				}
			}
			toEnable.add(EDIT_LEVELS);
		}
		enableMenuItems(popupMenu, toEnable);
	}
	
	private Rectangle determineTileRectangle() {
		int minX = Math.min(startTile.x, highlightTile.x);
		int minY = Math.min(startTile.y, highlightTile.y);
		int maxX = Math.max(startTile.x, highlightTile.x);
		int maxY = Math.max(startTile.y, highlightTile.y);
		return new Rectangle(minX, minY, 
				maxX - minX + 1, maxY - minY + 1);
	}
	
    private List<Point> determineTilePoints() {
    	List<Point> tilePoints = new ArrayList<Point>();
    	for (int x = highlightRectangle.x; x < highlightRectangle.x + highlightRectangle.width; x++) {
    		for (int y = highlightRectangle.y; y < highlightRectangle.y + highlightRectangle.height; y++) {
    			tilePoints.add(new Point(x, y));
    		}
		}
    	return tilePoints;
    }

	private void populatePopupMenu(Menu menu) {
		// dynamic options
		MenuItem sendToBack = new MenuItem(menu, SWT.PUSH);
		sendToBack.setText(SEND_TO_BACK);
		sendToBack.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				map.sendToBack(determineTilePoints());
				redraw();
			}
		});
		MenuItem keepTop = new MenuItem(menu, SWT.PUSH);
		keepTop.setText(KEEP_TOP);
		keepTop.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				map.keepTop(determineTilePoints());
				redraw();
				setLabelText();
			}
		});
		MenuItem clear = new MenuItem(menu, SWT.PUSH);
		clear.setText(CLEAR);
		clear.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				map.clear(determineTilePoints());
				redraw();
				setLabelText();
			}
		});
		
		// separator
		new MenuItem(menu, SWT.SEPARATOR);
		
		// edit options
		MenuItem editImages = new MenuItem(menu, SWT.PUSH);
		editImages.setText(EDIT_IMAGES);
		editImages.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				MapTile mapTile = map.getMapTile(highlightTile);
				TileEditDialog tileEditor = new TileEditDialog(DisplayHelper.getShell(), editImagesFactory);
				if (tileEditor.editTile(mapTile)) {
					setLabelText();
					// update the map image
					map.updateTileImage(mapTile, highlightTile);
					redraw();
				}
			}				
		});
		MenuItem editLevels = new MenuItem(menu, SWT.PUSH);
		editLevels.setText(EDIT_LEVELS);
		editLevels.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				MapTile mapTile = map.getMapTile(highlightTile);
				TileEditDialog tileEditor = new TileEditDialog(DisplayHelper.getShell(), editLevelsFactory, 240, 320);
				if (tileEditor.editTile(mapTile)) {
					// edit levels can be applied to a range of tiles
					for (Point tilePoint: determineTilePoints()) {
						map.getMapTile(tilePoint).setLevels(mapTile.getLevels());
					}
					setLabelText();			
				}
			}
		});
		MenuItem editMasks = new MenuItem(menu, SWT.PUSH);
		editMasks.setText(EDIT_MASKS);
		editMasks.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				MapTile mapTile = map.getMapTile(highlightTile);
				TileEditDialog tileEditor = new TileEditDialog(DisplayHelper.getShell(), editMasksFactory);
				if (tileEditor.editTile(mapTile)) {
					setLabelText();				
				}
			}
		});
	}
			
	private void enableMenuItems(Menu menu, Set<String> toEnable) {
		for (MenuItem menuItem: menu.getItems()) {
			if ((menuItem.getStyle() == SWT.PUSH) && (toEnable.contains(menuItem.getText()))) {
				menuItem.setEnabled(true);
			}
			else {
				menuItem.setEnabled(false);
			}
		}
	}
}
