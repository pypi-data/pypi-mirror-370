/// Universally applicable error rates and distances
pub fn universal_error_rate_array<T: PartialEq>(
    predictions: &Vec<&Vec<T>>,
    references: &Vec<&Vec<T>>,
) -> Vec<f64> {
    assert!(predictions.len() == references.len());
    return universal_edit_distance_array(predictions, references)
        .iter()
        .zip(references)
        .map(|(distance, reference)| (*distance as f64 / reference.len() as f64))
        .collect();
}

pub fn universal_edit_distance_array<T: PartialEq>(
    predictions: &Vec<&Vec<T>>,
    references: &Vec<&Vec<T>>,
) -> Vec<usize> {
    assert!(predictions.len() == references.len());
    predictions
        .iter()
        .zip(references.iter())
        .map(|(a, b)| universal_edit_distance(a, b))
        .collect()
}

pub fn universal_error_rate<T: PartialEq>(
    predictions: &Vec<&Vec<T>>,
    references: &Vec<&Vec<T>>,
) -> f64 {
    // This is the equivalent to the jiwer and evaluation package in Python
    // Takes the sum of the edit distances and divides it by total length of
    // the references.
    assert!(predictions.len() == references.len());
    let mut distance: usize = 0;
    let mut total: usize = 0;
    predictions
        .iter()
        .zip(references.iter())
        .for_each(|(prediction, reference)| {
            distance += universal_edit_distance(prediction, reference);
            total += reference.len()
        });
    (distance as f64) / (total as f64)
}

/// An actual implementation of the Levenshtein distance
pub fn universal_edit_distance<T: PartialEq>(left: &Vec<T>, right: &Vec<T>) -> usize {
    if left.len() == 0 {
        return right.len();
    }
    if right.len() == 0 {
        return left.len();
    }

    if left.len() < right.len() {
        return universal_edit_distance(right, left);
    }

    let len_right = right.len() + 1;
    let mut current_row = vec![0; len_right];
    for i in 1..len_right {
        current_row[i] = i;
    }

    let mut pre;
    let mut tmp;

    for (i, left_element) in left.iter().enumerate() {
        // get first column for this row
        pre = current_row[0];
        current_row[0] = i + 1;
        for (j, right_element) in right.iter().enumerate() {
            tmp = current_row[j + 1];
            current_row[j + 1] = std::cmp::min(
                // deletion
                tmp + 1,
                std::cmp::min(
                    // insertion
                    current_row[j] + 1,
                    // match or substitution
                    pre + if left_element == right_element { 0 } else { 1 },
                ),
            );
            pre = tmp;
        }
    }

    return current_row[len_right - 1];
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let reference = vec!["h", "e", "l", "l", "o"];
        let prediction = vec!["h", "e", "l", "o"];
        let result = universal_edit_distance(&reference, &prediction);
        assert_eq!(result, 1);
        let result = universal_edit_distance(&prediction, &reference);
        assert_eq!(result, 1);
        let result = universal_edit_distance(&vec![&prediction], &vec![&reference]);
        assert_eq!(1, result);
        let result = universal_error_rate(&vec![&prediction], &vec![&reference]);
        assert_eq!(0.2, result);
    }
}
