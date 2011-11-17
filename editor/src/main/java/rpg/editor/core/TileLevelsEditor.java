package rpg.editor.core;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.List;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;

import rpg.editor.Constants;
import rpg.editor.model.MapTile;
import rpg.editor.model.TileSet;

public class TileLevelsEditor extends TileEditor {
	
	private List levelsList;
	
	public TileLevelsEditor(Composite parent, MapTile mapTile) {
		this(parent, SWT.NONE, mapTile);
	}
	
	public TileLevelsEditor(Composite parent, int style, MapTile mapTile) {
		super(parent, style, mapTile);
		
		this.setLayout(new GridLayout());
		this.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		Group addLevelGroup = new Group(this, SWT.SHADOW_ETCHED_IN);
		addLevelGroup.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false));
		addLevelGroup.setLayout(new GridLayout(2, false));
		// new level text field
		final Text text = new Text(addLevelGroup, SWT.BORDER);
		text.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		// add button
		Button add = new Button(addLevelGroup, SWT.PUSH);
		add.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, false));
		add.setText("Add");
		
		Group levelsGroup = new Group(this, SWT.SHADOW_ETCHED_IN);
		levelsGroup.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		levelsGroup.setLayout(new GridLayout(2, false));
		levelsList = new List(levelsGroup, SWT.BORDER | SWT.SINGLE);
		levelsList.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		String[] levels = mapTile.getLevels();
		if (levels != null) {
			levelsList.setItems(levels);
		}

		Composite listButtons = new Composite(levelsGroup, SWT.NONE);
		listButtons.setLayout(new GridLayout());
		listButtons.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));
		
		Button remove = new Button(listButtons, SWT.PUSH);
		remove.setLayoutData(new GridData(SWT.CENTER, SWT.BOTTOM, false, false));
		remove.setText("Remove");

		Button clear = new Button(listButtons, SWT.PUSH);
		clear.setLayoutData(new GridData(SWT.CENTER, SWT.TOP, false, false));
		clear.setText("Clear");

		// add listener
		add.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				String level = text.getText().trim().toUpperCase();
				if (validateLevel(level)) {
					levelsList.add(level);
					text.setText(Constants.EMPTY);
				}
				else {
					System.out.println("Invalid level: " + level);
				}
			}
		});
		
		// remove listener
		remove.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				int index = levelsList.getSelectionIndex();
				if (index > -1) {
					levelsList.remove(index);
				}
			}
		});
		
		// clear listener
		clear.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				levelsList.setItems(new String[0]);
			}
		});
	}
	
	private boolean validateLevel(String level) {
		boolean valid = false;
		if (level.length() > 0) {
			if (level.startsWith(Constants.SPECIAL)) {
				// should look something like S1.5
				level = level.substring(1);
			}
			else if (level.startsWith(Constants.DOWN)) {
				// should look something like D3-2 
				level = level.substring(1);
				String[] levels = level.split(Constants.DASH);
				if (levels.length != 2) {
					return false;
				}
				level = levels[0];
				try {
					Integer.parseInt(levels[1]);
				}
				catch (Exception e) {
					return false;
				}
			}
			
			try {
				Float.parseFloat(level);
				valid = true;
			}
			catch (Exception e) {
				// leave as false
			}			
		}
		return valid;
	}
	
	@Override
	public void applyChanges() {
		MapTile mapTile = getMapTile();
		String[] levels = levelsList.getItems();
		if ((levels == null) || (levels.length == 0)) {
			mapTile.setLevels(null);
		}
		else {
			mapTile.setLevels(levels);
		}
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
		
		new TileLevelsEditor(shell, mapTile);
		
		// shell.pack();
		shell.setSize(280, 200);
		shell.open();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) display.sleep();
		}
		
		// dispose resources
		ImageHelper.dispose();
		display.dispose();
	}

}
