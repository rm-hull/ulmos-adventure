package rpg.editor.core;

public enum ViewSize {
	
	SMALL(1, 16, "Small"), MEDIUM(2, 32, "Medium"), LARGE(4, 64, "Large");
	
	private int scalar;
	
	private int tileSize;
	
	private String label;
	
	private ViewSize(int scalar, int tileSize, String label) {
		this.scalar = scalar;
		this.tileSize = tileSize;
		this.label = label;
	}
	
	public int getScalar() {
		return scalar;
	}

	public int getTileSize() {
		return this.tileSize;
	}

	public String getLabel() {
		return label;
	}
}
