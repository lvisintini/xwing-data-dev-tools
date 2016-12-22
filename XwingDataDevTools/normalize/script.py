from XwingDataDevTools.normalize import (
    foreign_keys, maneuvers, ids, custom_indentation, order, rename, gather
)


def main(order_fields=False):
    ids.AddShipsIds()

    rename.FieldRenamer()

    maneuvers.HugeShipManeuverNormalizer()
    maneuvers.LargeShipManeuverNormalizer()
    maneuvers.SmallShipManeuverNormalizer()

    foreign_keys.SourceShipsForeignKeyNormalization()
    foreign_keys.SourceUpgradesForeignKeyNormalization()
    foreign_keys.SourceConditionsForeignKeyNormalization()
    foreign_keys.SourcePilotsForeignKeyNormalization()

    foreign_keys.UpgradeConditionsForeignKeyNormalization()
    foreign_keys.UpgradeShipForeignKeyNormalization()
    foreign_keys.UpgradeShipsForeignKeyNormalization()  # In case it has been renamed

    foreign_keys.PilotConditionsForeignKeyNormalization()
    foreign_keys.PilotShipForeignKeyNormalization()

    gather.AddMissingSlots()
    gather.AddMissingAnnouncedDate()
    gather.AddMissingReleaseDate()

    if order_fields:
        order.set_preferred_order()

    custom_indentation.same_line_indent()


if __name__ == '__main__':
    main(False)
