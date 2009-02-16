package rpg.editor.model;

/**
 * Simple wrapper for tiles that facilitates storing mask data against them. 
 * @author seldred
 */
public class MaskTile {
	
	private Tile tile;
	
	private String maskLevel;
	
	public MaskTile(Tile tile) {
		this.tile = tile;
	}
	
	public MaskTile(Tile tile, String maskLevel) {
		this.tile = tile;
		this.maskLevel = maskLevel;
	}

	public Tile getTile() {
		return tile;
	}
	
	public String getMaskLevel() {
		return maskLevel;
	}

	public void setMaskLevel(String maskLevel) {
		this.maskLevel = maskLevel;
	}	
}
