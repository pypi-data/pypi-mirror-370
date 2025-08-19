use std::collections::HashMap;

use pyo3::pyclass;


#[pyclass(get_all)]
pub struct Alignment {
    index: usize,
    start: usize,
    end: usize
}

pub fn optimial_aligment<T: PartialEq>(hyp: &[T], ref_: &[T]) -> Vec<Alignment> {
    let hyp_len = hyp.len() + 1;
    let ref_len = ref_.len() + 1;

    let mut table = vec![0usize; hyp_len * ref_len];

    // Pre-fill
    for i in 1..ref_len {
        table[i] = i;
    }
    for i in 1..hyp_len {
        table[i * ref_len] = i;
    }

    // Fill in the table
    for r in 1..ref_len {
        for h in 1..hyp_len {
            let cost = if hyp[h - 1] == ref_[r - 1] { 0 } else { 1 };
            table[r + ref_len * h] = *[
                get_value(&table, ref_len, h as isize - 1, r as isize) + 1, // deletion
                get_value(&table, ref_len, h as isize, r as isize - 1) + 1, // insertion
                get_value(&table, ref_len, h as isize - 1, r as isize - 1) + cost, // substitution/match
            ]
            .iter()
            .min()
            .unwrap();
        }
    }

    // Backtracking
    let mut h = hyp_len - 1;
    let mut r = ref_len - 1;
    let mut tokens = Vec::new();

    while h > 0 && r > 0 {
        tokens.push((r - 1, h - 1));

        let del = get_value(&table, ref_len, h as isize - 1, r as isize);
        let ins = get_value(&table, ref_len, h as isize, r as isize - 1);
        let sub = get_value(&table, ref_len, h as isize - 1, r as isize - 1);

        let lowest = del.min(ins).min(sub);

        if del == lowest {
            h -= 1;
        } else if ins == lowest {
            r -= 1;
        } else {
            h -= 1;
            r -= 1;
        }
    }

    let mut map: HashMap<usize, Vec<usize>> = HashMap::new();

    for (ref_idx, hyp_idx) in tokens {
        map.entry(ref_idx).or_default().push(hyp_idx);
    }

    let mut result: Vec<Alignment> = map
        .into_iter()
        .map(|(ref_idx, hyp_indices)| {
            let min = *hyp_indices.iter().min().unwrap();
            let max = *hyp_indices.iter().max().unwrap();
            Alignment {
                index: ref_idx,
                start: min,
                end: max + 1,
            }
        })
        .collect();

    // Optional: sort by reference_index
    result.sort_by_key(|a| a.index);
    return result
}

fn get_value(table: &[usize], ref_len: usize, h: isize, r: isize) -> usize {
    // Helper function for indexing
    let h = h.max(0) as usize;
    let r = r.max(0) as usize;
    table[r + ref_len * h]
}
