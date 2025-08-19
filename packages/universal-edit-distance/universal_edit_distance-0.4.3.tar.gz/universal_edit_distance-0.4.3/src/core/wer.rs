use crate::core::uer;

pub(crate) fn split_strings_into_word_vec<'a>(list: &Vec<&'a str>) -> Vec<Vec<&'a str>> {
    return list
        .iter()
        .map(|x| x.split(" ").filter(|x| x.len() >= 1).collect())
        .collect::<Vec<Vec<&str>>>();
}

pub fn word_error_rate_array(predictions: &Vec<&str>, references: &Vec<&str>) -> Vec<f64> {
    let predictions_split = split_strings_into_word_vec(predictions);
    let references_split = split_strings_into_word_vec(references);
    uer::universal_error_rate_array(
        &predictions_split.iter().collect(),
        &references_split.iter().collect(),
    )
}

pub fn word_edit_distance_array(predictions: &Vec<&str>, references: &Vec<&str>) -> Vec<usize> {
    let predictions_split = split_strings_into_word_vec(predictions);
    let references_split = split_strings_into_word_vec(references);
    uer::universal_edit_distance_array(
        &predictions_split.iter().collect(),
        &references_split.iter().collect(),
    )
}

pub fn word_error_rate(predictions: &Vec<&str>, references: &Vec<&str>) -> f64 {
    let predictions_split = split_strings_into_word_vec(predictions);
    let references_split = split_strings_into_word_vec(references);
    uer::universal_error_rate(
        &predictions_split.iter().collect(),
        &references_split.iter().collect(),
    )
}
