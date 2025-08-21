def abbreviate_number(number):
    abbreviations = [
        (1e9, 'B'),
        (1e6, 'M'),
        (1e3, 'K')
    ]
    if not number:
        return 'N/A'
    else:
        number = float(number)

        if number < 1000:
            return str(int(number))

        for factor, suffix in abbreviations:
            if number >= factor:
                if number == factor:  # Exactly 1 billion (or other thresholds)
                    abbreviated = f"1{suffix}"
                else:
                    abbreviated = f"{number / factor:.1f}{suffix}"

                return abbreviated

        return str(number)