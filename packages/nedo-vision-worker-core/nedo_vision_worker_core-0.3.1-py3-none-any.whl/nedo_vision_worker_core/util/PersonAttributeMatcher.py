from .BoundingBoxMetrics import BoundingBoxMetrics

EXCLUSIVE_LABEL_GROUPS = [
    ("helmet", "no_helmet"),
    ("vest", "no_vest"),
    ("gloves", "no_gloves"),
    ("goggles", "no_goggles"),
    ("boots", "no_boots"),
]

MULTI_INSTANCE_CLASSES = ["boots", "gloves", "goggles", "no_gloves"]

NEGATIVE_CLASSES = ["no_helmet", "no_vest", "no_goggles", "no_boots"]

class PersonAttributeMatcher:
    @staticmethod
    def match_persons_with_attributes(persons, attributes, coverage_threshold=0.2):
        matched_results = []

        exclusive_groups = []
        for group in EXCLUSIVE_LABEL_GROUPS:
            exclusive_groups.append(set(group))
        exclusive_labels = set(l for group in EXCLUSIVE_LABEL_GROUPS for l in group)

        for person in persons:
            person_bbox = person["bbox"]
            matched_attributes = []
            for attr in attributes:
                attr_bbox = attr["bbox"]
                coverage = BoundingBoxMetrics.compute_coverage(person_bbox, attr_bbox)
                if coverage >= coverage_threshold:
                    matched_attributes.append({
                        "label": attr["label"],
                        "confidence": attr["confidence"],
                        "coverage": round(coverage, 2),
                        "bbox": attr_bbox
                    })
            
            filtered_attributes = []
            
            for group in exclusive_groups:
                group_attrs = [a for a in matched_attributes if a["label"] in group]
                if group_attrs:
                    best = max(group_attrs, key=lambda a: a["confidence"])
                    filtered_attributes.append(best)

            for attr in matched_attributes:
                label = attr["label"]
                is_in_exclusive_group = any(label in group for group in exclusive_groups)
                if is_in_exclusive_group:
                    continue
                if label in MULTI_INSTANCE_CLASSES:
                    filtered_attributes.append(attr)
            
            for attr in matched_attributes:
                label = attr["label"]
                if label in MULTI_INSTANCE_CLASSES and label not in NEGATIVE_CLASSES:
                    already_added = any(
                        a["label"] == label and list(a["bbox"]) == list(attr["bbox"]) 
                        for a in filtered_attributes
                    )
                    if not already_added:
                        filtered_attributes.append(attr)
            matched_results.append({
                "label": "person",
                "confidence": person["confidence"],
                "bbox": person_bbox,
                "attributes": filtered_attributes
            })
        return matched_results
