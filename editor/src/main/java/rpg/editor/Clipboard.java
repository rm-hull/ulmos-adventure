package rpg.editor;

import rpg.editor.model.MapSnapshot;

public class Clipboard {
	
	private MapSnapshot mapSnapshot;
	
	// == SINGLETON ==
	
	private static Clipboard instance = new Clipboard();
	
	private Clipboard() {
	}

	public static Clipboard getInstance() {
		return instance;
	}

	// ===============
	
	public MapSnapshot getMapSnapshot() {
		return mapSnapshot;
	}

	public void setMapSnapshot(MapSnapshot mapSnapshot) {
		this.mapSnapshot = mapSnapshot;
	}
	
	public boolean containsData() {
		if (mapSnapshot == null) {
			return false;
		}
		return true;
	}
}
