class BoundingBoxMetrics:
    """Computes IoU and coverage for bounding boxes."""

    @staticmethod
    def compute_iou(box1, box2):
        """
        Computes Intersection over Union (IoU) between two bounding boxes.
        Args:
            box1, box2: [x1, y1, x2, y2] (coordinates of two bounding boxes)
        Returns:
            IoU score (float between 0 and 1)
        """
        x1, y1, x2, y2 = box1
        x1_p, y1_p, x2_p, y2_p = box2

        # Compute intersection
        inter_x1 = max(x1, x1_p)
        inter_y1 = max(y1, y1_p)
        inter_x2 = min(x2, x2_p)
        inter_y2 = min(y2, y2_p)

        inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)

        # Compute union
        box1_area = (x2 - x1) * (y2 - y1)
        box2_area = (x2_p - x1_p) * (y2_p - y1_p)
        union_area = box1_area + box2_area - inter_area

        return inter_area / union_area if union_area > 0 else 0

    @staticmethod
    def compute_coverage(box1, box2):
        """
        Computes the coverage percentage of box2 inside box1.
        Coverage is defined as the intersection area over box2's area.
        Args:
            box1, box2: [x1, y1, x2, y2] (coordinates of two bounding boxes)
        Returns:
            Coverage ratio (float between 0 and 1)
        """
        x1, y1, x2, y2 = box1
        x1_o, y1_o, x2_o, y2_o = box2

        # Compute intersection
        inter_x1 = max(x1, x1_o)
        inter_y1 = max(y1, y1_o)
        inter_x2 = min(x2, x2_o)
        inter_y2 = min(y2, y2_o)

        inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
        box2_area = (x2_o - x1_o) * (y2_o - y1_o)

        return inter_area / box2_area if box2_area > 0 else 0
