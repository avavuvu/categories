export interface Category {
	label: string;
	table: string;
	query?: string;
	fuzzy?: boolean;
	facts?: string;
	valid_letters: string[];
}
