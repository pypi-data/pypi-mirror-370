use itertools::izip;

pub fn poi_error_rate<T: PartialEq>(
    predictions: &[&[T]],
    references: &[&[T]],
    point_of_interests: &[&[bool]],
) -> f64 {
    assert!(
        predictions.len() == references.len(),
        "length of predictions not the same as references"
    );
    let mut distance: usize = 0;
    let mut total: usize = 0;
    izip!(predictions, references, point_of_interests).for_each(|(prediction, reference, pois)| {
        distance += poi_edit_distance(prediction, reference, pois);
        total += pois.iter().filter(|b| **b).count();
    });
    (distance as f64) / (total as f64)
}

pub fn poi_edit_distance<T: PartialEq>(hyp: &[T], ref_: &[T], poi: &[bool]) -> usize {
    assert_eq!(
        poi.len(),
        ref_.len(),
        "Points of interests not the same length as reference"
    );

    // Edge case where the hypothesis is empty
    if hyp.is_empty() {
        return poi.iter().filter(|b| **b).count()
    }

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
    let mut edit_distance = 0;

    while h > 0 || r > 0 {
        if poi[r - 1] && ref_[r - 1] != hyp[h - 1] {
            edit_distance += 1;
        }
        let del = get_value(&table, ref_len, h as isize - 1, r as isize);
        let ins = get_value(&table, ref_len, h as isize, r as isize - 1);
        let sub = get_value(&table, ref_len, h as isize - 1, r as isize - 1);

        let lowest = del.min(ins).min(sub);

        if del == lowest {
            h -= 1;
        } else if ins == lowest {
            r -= 1;
        } else {
            h = (h as isize - 1).max(0) as usize;
            r = (r as isize - 1).max(0) as usize;
        }
    }

    return edit_distance;
}

fn get_value(table: &[usize], ref_len: usize, h: isize, r: isize) -> usize {
    // Helper function for indexing
    let h = h.max(0) as usize;
    let r = r.max(0) as usize;
    table[r + ref_len * h]
}
