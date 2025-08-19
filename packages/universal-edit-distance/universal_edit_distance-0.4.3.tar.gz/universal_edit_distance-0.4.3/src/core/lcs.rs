pub fn longest_common_subsequence<T: PartialEq>(left: &Vec<T>, right: &Vec<T>) -> usize {
    if left.len() == 0 {
        return 0;
    }
    if right.len() == 0 {
        return 0;
    }

    if left.len() < right.len() {
        return longest_common_subsequence(right, left);
    }

    let len_right = right.len() + 1;
    let mut current_row = vec![0; len_right];

    for (i, left_element) in left.iter().enumerate() {
        // get first column for this row
        for (j, right_element) in right.iter().enumerate() {
            current_row[j + 1] = std::cmp::max(current_row[j + 1], current_row[j]);
            if left_element == right_element {
                current_row[j + 1] += 1;
            }
        }
    }

    return current_row[len_right - 1];
}
