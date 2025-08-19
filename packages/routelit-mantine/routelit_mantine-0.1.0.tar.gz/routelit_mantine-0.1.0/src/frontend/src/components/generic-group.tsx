import { Flex } from "@mantine/core";
import React from "react";

interface GenericGroupProps {
  children?: React.ReactNode;
  groupProps?: React.ComponentProps<typeof Flex>;
  options?: Array<{
    label: string;
    value: string;
  }>;
  renderGroup: (children: React.ReactNode, props: Record<string, unknown>) => React.ReactNode;
  renderItem: (item: { label: string; value: string }) => React.ReactNode;
  [key: string]: unknown;
}

function GenericGroup({
  children,
  options,
  groupProps,
  renderGroup,
  renderItem,
  ...props
}: GenericGroupProps) {
  const content = (
    <>
      {children}
      {options && (
        <Flex gap="sm" {...groupProps}>
          {options?.map((item) => renderItem(item))}
        </Flex>
      )}
    </>
  );

  return <>{renderGroup(content, props)}</>;
}

export default GenericGroup;
