import {
  ActionIcon as MantineActionIcon,
  ActionIconProps,
} from "@mantine/core";
import DynamicTablerIcon from "./icon";

interface IActionIconProps extends ActionIconProps {
  name: string;
}

export function ActionIcon({ name, ...props }: IActionIconProps) {
  return (
    <MantineActionIcon {...props}>
      <DynamicTablerIcon name={name} />
    </MantineActionIcon>
  );
}
