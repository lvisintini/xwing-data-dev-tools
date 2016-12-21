from XwingDataDevTools.normalize import foreign_keys, trivial, maneuvers, ids, custom_indentation


def main():
    ids.AddShipsIds()

    maneuvers.HugeShipManeuverNormalizer()
    maneuvers.LargeShipManeuverNormalizer()
    maneuvers.SmallShipManeuverNormalizer()

    foreign_keys.SourceShipsForeignKeyNormalization()
    foreign_keys.SourceUpgradesForeignKeyNormalization()
    foreign_keys.SourceConditionsForeignKeyNormalization()
    foreign_keys.SourcePilotsForeignKeyNormalization()

    foreign_keys.UpgradeConditionsForeignKeyNormalization()
    foreign_keys.UpgradeShipsForeignKeyNormalization()

    foreign_keys.PilotConditionsForeignKeyNormalization()
    foreign_keys.PilotShipForeignKeyNormalization()

    trivial.AddMissingSlots()

    custom_indentation.same_line_indent()


if __name__ == '__main__':
    main()
